"""
Example of metadata:
{'album': u'Let It Die', 
 'status': None, 
 'artist': u'Feist',
 'year': '9999', 
 'bitrate': 192, 
 'type': None, 
 'fingerprint': u'foo', 
 'title': u'Gatekeeper', 
 'echoprint_version': 4.12,  
 'albumid': None, 
 'artistid': None, 
 'is_valid': True, 
 'genres:['genre1', 'genre2'],
 'echonest_id': u'SOEUFFD12A6D4FBDF5', 
 'lastfm_id': u'10577496'
 'album_lastfm_id: 'foo'
 'lastfm_data': {
          album:{
               artist:u'Feist', 
               image:['http://userserve-ak.last.fm/serve/64s/67147752.png',                     
                      'http://userserve-ak.last.fm/serve/126/67147752.png',           
               mbid:u'49683c30-b73d-40cf-a370-a8d1224be26c',]
               position:u'1', 
               title:u'Let It Die', 
               url:u'http://www.last.fm/music/Feist/Let+It+Die'
          }, 
          artist:[{
               mbid:u'a670e05a-cea8-4b37-bce9-d82daf1a0fa4', 
               name:u'Feist', url:u'http://www.last.fm/music/Feist'
          }], 
          duration:u'135000', 
          id:u'10577496', 
          listeners:u'247404', 
          mbid:'', 
          name:u'Gatekeeper', 
          playcount:u'1402368', 
          streamable:{fulltrack:u'0', data:u'0'}, 
          toptags:{
             tag:[
                    {name:u'indie', url:u'http://www.last.fm/tag/indie'}, 
                    {name:u'female vocalists', url:u'http://www.last.fm/tag/female%20vocalists'}, 
                    {name:u'singer-songwriter', url:u'http://www.last.fm/tag/singer-songwriter'}, 
                    {name:u'canadian', url:u'http://www.last.fm/tag/canadian'}, 
                    {name:u'indie pop', url:u'http://www.last.fm/tag/indie%20pop'}]},                
          url:u'http://www.last.fm/music/Feist/_/Gatekeeper'}, 
 'echonest_data': {
     u'title': u'Gatekeeper', 
     u'tag': 0, u'artist_name': 
     u'Feist', 
     u'artist_id': u'AR6NRQI1187FB37544', 
     u'score': 289, 
     u'message': u'OK (match type 6)', 
     u'id': u'SOEUFFD12A6D4FBDF5', 
     u'audio_summary': {
          u'key': 9, 
          u'analysis_url': u'foo', 
          u'energy': 0.1101314618849576, 
          u'tempo': 109.88, 
          u'mode': 0, 
          u'time_signature': 4, 
          u'duration': 136.67946, 
          u'loudness': -17.391, 
          u'audio_md5': u'0d7ae34872b9da1237a7bf172d958594', 
          u'danceability': 0.8138518719248211}}, 
}

"""
from django.conf import settings
from django.db.models.query_utils import Q
from shutil import rmtree
from tempfile import mkdtemp
from yabase.models import SongMetadata
from yaref.models import YasoundSong, YasoundArtist, YasoundAlbum, YasoundGenre, \
    YasoundSongGenre, build_mongodb_index
from yaref.utils import get_simplified_name, convert_filename_to_filepath
import datetime
import hashlib
import logging
import os
import random
import requests
import uploader
import uuid
import subprocess as sub
from django.utils.translation import ugettext_lazy as _
import shutil
from decimal import *

logger = logging.getLogger("yaapp.yabase")

class SongImporter:
    _messages = u''
        
    def _log(self, message):
        logger.info(unicode(message))
        self._messages = u'%s\n%s' % (self._messages, message)
        
    def _find_echonest_id_for_artist(self, metadata):
        data = metadata.get('echonest_data')
        if not data:
            return None
        return data.get('artist_id')
    
    def _find_mb_id_for_song(self, metadata):
        if not metadata['lastfm_data']:
            return None
        return metadata.get('mbid')
    
    def _find_mb_id_for_artist(self, metadata):
        lastfm_data = metadata.get('lastfm_data')
        if not lastfm_data:
            return None
        
        artist = lastfm_data.get('artist')
        if not artist:
            return None
        
        return artist[0].get('mbid')
    
    
    def _find_mb_id_for_album(self, metadata):
        lastfm_data = metadata.get('lastfm_data')
        if not lastfm_data:
            return None
        
        album = lastfm_data.get('album')
        if not album:
            return None
        
        return album.get('mbid')
    
    def _find_cover_url_for_album(self, metadata):
        lastfm_data = metadata.get('lastfm_data')
        if not lastfm_data:
            return None
        
        album = lastfm_data.get('album')
        if not album:
            return None
        
        image = album.get('image')
        if not image:
            return None
        
        return image[-1]
    
    def _find_audio_summary(self, metadata):
        data = metadata.get('echonest_data')
        if not data:
            return None
        return data.get('audio_summary')
    
    def _find_audio_summary_item(self, metadata, item, default=None):
        audio_summary = self._find_audio_summary(metadata)
        if not audio_summary:
            return default
        return audio_summary.get(item)
    
    def _generate_filename_and_path_for_song(self):
        path_exists = True
        filename = None
        while path_exists:
            filename = ''.join(random.choice("01234567890abcdef") for i in xrange(9)) + '.mp3'
            path = os.path.join(settings.SONGS_ROOT, convert_filename_to_filepath(filename))
            path_exists = os.path.exists(path)
        return filename, path
    
    def _generate_filename_and_path_for_cover(self, url):
        extension = url[-4:len(url)]
        path_exists = True
        filename = None
        while path_exists:
            filename = ''.join(random.choice("01234567890abcdef") for i in xrange(9)) + extension
            path = os.path.join(settings.ALBUM_COVERS_ROOT, convert_filename_to_filepath(filename))
            path_exists = os.path.exists(path)
        return filename, path
    
    def _get_filepath_for_preview(self, filepath):
        name, extension = os.path.splitext(filepath)
        preview = u'%s_preview64%s' % (name, extension)
        return preview
     
    def _generate_preview(self, source, destination):
        self._log('generating preview for %s' % (source))
        args = [settings.FFMPEG_BIN, 
                '-i',
                source]
        args.extend(settings.FFMPEG_GENERATE_PREVIEW_OPTIONS.split(" "))
        args.append(destination)
        p = sub.Popen(args,stdout=sub.PIPE,stderr=sub.PIPE)
        output, errors = p.communicate()
        if len(errors) == 0:
            self._log(errors)
            return False
        return True    
        
    def _get_quality(self, metadata):
        quality = 0;
        bitrate = int(metadata.get('bitrate'))
        echonest_id = metadata.get('echonest_id')
        lastfm_id = metadata.get('lastfm_id')
        if bitrate >= 192:
            quality = 100
        if lastfm_id:
            quality += 1
        if echonest_id:
            quality += 1
        return quality
        
    def _get_or_create_artist(self, metadata):
        echonest_id = self._find_echonest_id_for_artist(metadata)
        if not echonest_id:
            self._log(_("no echonest info about artist"))
            return None
        mb_id = self._find_mb_id_for_artist(metadata)
        name = metadata.get('artist')
        name_simplified = get_simplified_name(name)
        
        if not (echonest_id or mb_id or name):
            self._log(_("artist info not sufficient"))
            return None
        
        try:
            artist = YasoundArtist.objects.get(echonest_id=echonest_id)
        except YasoundArtist.DoesNotExist:
            self._log(_("creating new artist (echonest_id=%s): %s") % (echonest_id, name))
            artist = YasoundArtist(echonest_id=echonest_id,
                                   musicbrainz_id=mb_id,
                                   name=name,
                                   name_simplified=name_simplified)
            artist.save()
        return artist
    
    def _get_or_create_album(self, metadata):
        lastfm_id = metadata.get('album_lastfm_id')
        if not lastfm_id:
            self._log(_("no lastfm info about album"))
            return None
        
        try:
            album = YasoundAlbum.objects.get(lastfm_id=lastfm_id)
            self._log(_("album already in database (%d)") % (album.id))
            return album
        except YasoundAlbum.DoesNotExist:
            pass
        
        mbid = self._find_mb_id_for_album(metadata)
        name = metadata.get('album')
        self._log("creating new album: %s" % (name))
        name_simplified = get_simplified_name(name)
        cover_filename = None
        cover_url = self._find_cover_url_for_album(metadata)
        if cover_url:
            # saving cover
            cover_filename, cover_path = self._generate_filename_and_path_for_cover(cover_url)
            r = requests.get(cover_url)
            self._log(_("downloading album cover"))
            if r.status_code == 200:
                image_data = r.content
                os.makedirs(os.path.dirname(cover_path))
                destination = open(cover_path, 'wb')
                destination.write(image_data)
                destination.close()  
        
        album = YasoundAlbum(lastfm_id=lastfm_id,
                             musicbrainz_id=mbid,
                             name=name,
                             name_simplified=name_simplified,
                             cover_filename=cover_filename)
        album.save()
        
        return album
    
    def _convert_to_mp3(self, source, destination):
        self._log("converting to mp3 : %s -> %s" % (source, destination))
        args = [settings.FFMPEG_BIN, 
                '-i',
                source]
        args.extend(settings.FFMPEG_CONVERT_TO_MP3_OPTIONS.split(" "))
        args.append(destination)
        p = sub.Popen(args,stdout=sub.PIPE,stderr=sub.PIPE)
        output, errors = p.communicate()
        print output
        print errors
        if len(errors) == 0:
            self._log(errors)
            return False
        return True    
    
        
    def get_messages(self):
        return self._messages
    
    def import_song(self, binary, metadata=None, convert=True):
        """
        import song without metadata
        """
        directory = mkdtemp()
        path, extension = os.path.splitext(binary.name)
        
        source = u'%s/s%s' % (directory, extension)
        destination = u'%s/d.mp3' % (directory)
        source_f = open(source , 'wb')
        for chunk in binary.chunks():
            source_f.write(chunk)
        source_f.close()
            
        if convert==True:
            self._convert_to_mp3(source, destination)
            if not metadata:
                metadata = uploader.get_file_infos(destination)
            sm, messages = self.process_song(metadata, filepath=destination)
        else:
            if not metadata:
                metadata = uploader.get_file_infos(source)
            sm, messages = self.process_song(metadata, binary=binary)
            
        rmtree(directory)
        
        return sm, messages
    
    def _find_song_by_echonest_id(self, echonest_id):
        if not echonest_id:
            return None
        try:
            return YasoundSong.objects.filter(echonest_id=echonest_id)[0]
        except:
            return None
        
    def _find_song_by_lastfm_id(self, lastfm_id):
        if not lastfm_id:
            return None
        try:
            return YasoundSong.objects.filter(lastfm_id=lastfm_id)[0]
        except:
            return None

    def process_song(self, metadata, binary=None, filepath=None):
        """
        * import song file, 
        * create YasoundSong, 
        * create YasoundArtist 
        * create YasoundAlbum
        * create SongMetadata
        * finally return SongMetadata
        
        """
        name = metadata.get('title')
        artist_name = metadata.get('artist')
        album_name = metadata.get('album')
    
        self._log("importing %s-%s-%s" % (name, album_name, artist_name))
    
        echonest_data = metadata.get('echonest_data')
        lastfm_data = metadata.get('lastfm_data')
        if not echonest_data and not lastfm_data:
            self._log("no echonest and lastfm datas")
            return None, self.get_messages()
        fingerprint = metadata.get('fingerprint')
        if not fingerprint:
            self._log("no fingerprint")
            return None, self.get_messages()
        fingerprint_hash = hashlib.sha1(fingerprint).hexdigest()
        
        now = datetime.datetime.today()
        
        if not name:
            logger.error("no title")
            return None, self.get_messages()
        name_simplified = get_simplified_name(name)
        artist_name_simplified = get_simplified_name(artist_name)
        album_name_simplified = get_simplified_name(album_name)
        
        loudness = self._find_audio_summary_item(metadata, 'loudness', 0)
        danceability = self._find_audio_summary_item(metadata, 'danceability', 0)
        energy = self._find_audio_summary_item(metadata, 'energy', 0)
        tempo = self._find_audio_summary_item(metadata, 'tempo', 0)
        tonality_mode = self._find_audio_summary_item(metadata, 'mode', 0)
        tonality_key = self._find_audio_summary_item(metadata, 'key', 0)
        echoprint_version = metadata.get('echoprint_version')
        
        echonest_id = metadata.get('echonest_id')
        lastfm_id = metadata.get('lastfm_id')
        musicbrainz_id = self._find_mb_id_for_song(metadata)
        duration = metadata.get('duration')
        quality = self._get_quality(metadata)

        self._log(_('echonest id = %s, lastfm_id = %s, musicbrainz_id = %s') % (echonest_id, lastfm_id, musicbrainz_id))
        
        # first check for an existing SongMetadata
        try:
            sm = SongMetadata.objects.get(name=name, artist_name=artist_name, album_name=album_name)
            if sm.yasound_song_id:
                try:
                    YasoundSong.objects.get(id=sm.yasound_song_id)
                    self._log(_("song already in database: %s") % (sm.yasound_song_id))
                    return None, self.get_messages()
                except YasoundSong.DoesNotExist:
                    self._log(_("song metadata already in database, but no YasoundSong"))
        except SongMetadata.DoesNotExist:
            sm = SongMetadata(name=name, artist_name=artist_name, album_name=album_name)
            sm.save()
            self._log(_('creating SongMetadata, id = %s') % (sm.id))
    
        # create artist with info from echonest and lastfm
        self._log(_('looking for artist'))
        artist = self._get_or_create_artist(metadata)
        # create album if found on lastfm
        self._log(_('looking for album'))
        album = self._get_or_create_album(metadata)
        
        # create yasound song
        self._log(_('looking for song'))
        found = self._find_song_by_echonest_id(echonest_id)
        if not found:
            found = self._find_song_by_lastfm_id(lastfm_id)
        if found:
            song = found
            self._log("Song already existing in database (id=%s)" % (song.id))
        else:
            # generate filename and save binary to disk
            self._log(_('generating filename'))
            filename, mp3_path = self._generate_filename_and_path_for_song()
            os.makedirs(os.path.dirname(mp3_path))
            
            # create song object
            self._log(_('creating YasoundSong'))
            song = YasoundSong(artist=artist,
                               album=album,
                               echonest_id=echonest_id,
                               lastfm_id=lastfm_id,
                               musicbrainz_id=musicbrainz_id,
                               filename=filename,
                               filesize=0,
                               name=name,
                               name_simplified=name_simplified,
                               artist_name=artist_name,
                               artist_name_simplified=artist_name_simplified,
                               album_name=album_name,
                               album_name_simplified=album_name_simplified,
                               duration=duration,
                               danceability=Decimal(str(danceability)),
                               loudness=Decimal(str(loudness)),
                               energy=Decimal(str(energy)),
                               tempo=int(tempo),
                               tonality_mode=tonality_mode,
                               tonality_key=tonality_key,
                               fingerprint=fingerprint,
                               fingerprint_hash=fingerprint_hash,
                               echoprint_version=echoprint_version,
                               publish_at=None,
                               published=False,
                               locked=False,
                               quality=quality)
            song.save()
            self._log(_('YasoundSong generated, id = %s') % (song.id))
            
            self._log(_('generating file data'))
            if binary:
                destination = open(mp3_path, 'wb')
                for chunk in binary.chunks():
                    destination.write(chunk)
                destination.close()  
                self._log("generated mp3 file : %s" % (mp3_path))
            elif filepath:
                shutil.copy(filepath, mp3_path)
                self._log("copied %s to %s" % (filepath, mp3_path))
                
            # generate 64kb preview
            self._log(_('generating preview'))
            mp3_preview_path = self._get_filepath_for_preview(mp3_path)
            self._generate_preview(mp3_path, mp3_preview_path)
            self._log("generated mp3 preview file : %s" % (mp3_preview_path))
            
            song.filesize = os.path.getsize(mp3_path)
            song.save()
            
        # assign genre
        genres = metadata.get('genres')
        if genres:
            for genre in genres:
                genre_canonical = get_simplified_name(genre)
                yasound_genre, created = YasoundGenre.objects.get_or_create(name_canonical=genre_canonical, defaults={'name': genre})
                if created:
                    self._log("creating genre: %s" % (genre))
                song_genre, created = YasoundSongGenre.objects.get_or_create(song=song, genre=yasound_genre)
                if created:
                    self._log("genre %s associated with song %s" % (genre, song))
                    
        
        # assign song id to metadata
        sm.yasound_song_id = song.id
        sm.save()
        self._log(_('Association between YasoundSong and SongMetadata done'))
        
        self._log(_('Building mongodb index'))
        build_mongodb_index()
        return sm, self.get_messages()
    

def import_song(binary, metadata, convert):    
    importer = SongImporter()
    return importer.import_song(binary, metadata, convert)
    
    
    
    