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
from decimal import *
from django.conf import settings
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _
from yabase.models import SongMetadata, Radio, SongInstance
from yaref.models import YasoundSong, YasoundArtist, YasoundAlbum, YasoundGenre, \
    YasoundSongGenre
from yasearch.models import build_mongodb_index
from yaref.utils import convert_filename_to_filepath
from yasearch.utils import get_simplified_name
from yacore.database import flush_transaction
import datetime
import hashlib
import logging
import os, errno
import random
import requests
import shutil
import subprocess as sub
import uploader
import uuid
import mimetypes
import md5

logger = logging.getLogger("yaapp.yabase")

class SongImporter:
    """
    Helper class which allow to import & extract cover
    """
    
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
        lastfm_data = metadata.get('lastfm_data')
        if not lastfm_data:
            return None
        
        mbid = lastfm_data.get('mbid')
        if not mbid:
            return None
        
        if type(mbid) == type([]):
            return mbid[0]
        else:
            return mbid
    
    def _find_lastfm_fingerprintid(self, metadata):
        lastfm_data = metadata.get('lastfm_data')
        if not lastfm_data:
            return None
        return lastfm_data.get('fingerprintid')

    def _find_lastfm_rank(self, metadata):
        lastfm_data = metadata.get('lastfm_data')
        if not lastfm_data:
            return None
        rank = 0.0
        try:
            rank = float(lastfm_data.get('rank'))
        except:
            pass
        return rank
    
    def _find_mb_id_for_artist(self, metadata):
        lastfm_data = metadata.get('lastfm_data')
        if not lastfm_data:
            return None
        
        artist = lastfm_data.get('artist')
        if not artist:
            return None
        
        if type(artist) == type([]):
            return artist[0].get('mbid')
        else:
            return artist.get('mbid')
    
    
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
            filename = ''.join(random.choice("01234567890abcdef") for _i in xrange(9)) + '.mp3'
            path = os.path.join(settings.SONGS_ROOT, convert_filename_to_filepath(filename))
            path_exists = os.path.exists(path)
        return filename, path
    
    def _generate_filename_and_path_for_album_cover(self, url):
        extension = url[-4:len(url)]
        path_exists = True
        filename = None
        while path_exists:
            filename = ''.join(random.choice("01234567890abcdef") for _i in xrange(9)) + extension
            path = os.path.join(settings.ALBUM_COVERS_ROOT, convert_filename_to_filepath(filename))
            path_exists = os.path.exists(path)
        return filename, path
    
    def _generate_filename_and_path_for_song_cover(self, extension='.jpg'):
        path_exists = True
        filename = None
        while path_exists:
            filename = ''.join(random.choice("01234567890abcdef") for _i in xrange(9)) + extension
            path = os.path.join(settings.SONG_COVERS_ROOT, convert_filename_to_filepath(filename))
            path_exists = os.path.exists(path)
        return filename, path
    
        
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
        
        if not (echonest_id or mb_id or name):
            self._log(_("artist info not sufficient"))
            return None

        if name is None:
            self._log(_("no name for artist"))
            return None
            
        name_simplified = get_simplified_name(name)
        
        try:
            artist = YasoundArtist.objects.get(echonest_id=echonest_id)
        except YasoundArtist.DoesNotExist:
            self._log("creating new artist (echonest_id=%s): %s" % (echonest_id, name))
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
        if name is None:
            self._log("no name for album")
            return None
            
        self._log("creating new album: %s" % (name))
        name_simplified = get_simplified_name(name)
        cover_filename = None
        cover_url = self._find_cover_url_for_album(metadata)
        if cover_url:
            # saving cover
            cover_filename, cover_path = self._generate_filename_and_path_for_album_cover(cover_url)
            r = requests.get(cover_url)
            self._log(_("downloading album cover"))
            if r.status_code == 200:
                image_data = r.content
                try:
                    os.makedirs(os.path.dirname(cover_path))
                except OSError as e:
                    if e.errno == errno.EEXIST:
                        pass
                    else: raise
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
    
    def import_song(self, filepath, metadata=None, convert=True, allow_unknown_song=False, song_metadata_id=None):
        """
        import song without metadata
        """
        
        directory = os.path.dirname(filepath)
        destination = u'%s/d.mp3' % (directory)

        if convert==True:
            self._convert_to_mp3(filepath, destination)
            metadata = uploader.get_file_infos(destination, metadata)
            sm, messages = self.process_song(metadata, 
                                             filepath=destination, 
                                             allow_unknown_song=allow_unknown_song,
                                             song_metadata_id=song_metadata_id)
        else:
            metadata = uploader.get_file_infos(filepath, metadata)
            sm, messages = self.process_song(metadata, 
                                             filepath=filepath, 
                                             allow_unknown_song=allow_unknown_song,
                                             song_metadata_id=song_metadata_id)
            
        return sm, messages
    
    def _find_song_by_echonest_id(self, echonest_id):
        if not echonest_id:
            return None
        try:
            return YasoundSong.objects.filter(echonest_id=echonest_id)[0]
        except:
            return None
        
    def _find_songs_by_echonest_id(self, echonest_id):
        if not echonest_id:
            return []
        try:
            return YasoundSong.objects.filter(echonest_id=echonest_id)
        except:
            return []

    def _find_song_by_lastfm_id(self, lastfm_id):
        if not lastfm_id:
            return None
        try:
            return YasoundSong.objects.filter(lastfm_id=lastfm_id)[0]
        except:
            return None

    def _find_songs_by_lastfm_id(self, lastfm_id):
        if not lastfm_id:
            return []
        try:
            return YasoundSong.objects.filter(lastfm_id=lastfm_id)
        except:
            return []

    def _create_song_instance(self, sm, metadata):
        if not sm:
            self._log('no SongMetadata for _create_song_instance')
            return
        if not metadata:
            self._log('no metadata for _create_song_instance')
            return
        radio_id = metadata.get('radio_id')
        if not radio_id:
            self._log('no radio_id found for _create_song_instance')
            return
        
        radio = None
        try:
            radio = Radio.objects.get(id=radio_id)
        except:
            self._log('cannot find radio %s' % (radio_id))
            return
        
        playlist, _created = radio.get_or_create_default_playlist()
        if not playlist:
            self._log('cannot create playlist for radio id %s' % (radio_id))
            return
        
        si, _created = SongInstance.objects.get_or_create(metadata=sm, 
                                                         playlist=playlist)
        if sm.yasound_song_id is not None:
            self._log(u'activating radio %s' % radio)
            radio.ready = True
            radio.save()
        
        return si
    
    def _get_owner_id(self, metadata, echonest_id, lastfm_id):
        radio_id = metadata.get('radio_id')
        if not radio_id:
            return None
        if echonest_id is None and lastfm_id is None:
            try:
                radio = Radio.objects.get(id=radio_id)
                creator = radio.creator
                return creator.id
            except:
                return None
            

    def _find_server_version(self, metadata):
        lastfm_id = metadata.get('lastfm_id')
        
        candidates =  self._find_songs_by_lastfm_id(lastfm_id)
        if len(candidates) == 0:
            return None

        for candidate in candidates:
            song = candidate
            if not song.file_exists():
                return song
        return None

    def process_song(self, metadata, filepath=None, allow_unknown_song=False, song_metadata_id=None):
        """
        * import song file, 
        * create YasoundSong, 
        * create YasoundArtist 
        * create YasoundAlbum
        * create SongMetadata
        * finally return SongMetadata
        
        """
        name = metadata.get('title')
        artist_name = metadata.get('artist', u'')
        album_name = metadata.get('album', u'')
        filename = metadata.get('filename')
        
        if artist_name is None:
            artist_name = u''
        if album_name is None:
            album_name = u''
        
        self._log("importing %s-%s-%s" % (name, album_name, artist_name))
        
        is_valid = metadata.get('is_valid')
        if not is_valid:
            self._log("invalid file")
            return None, self.get_messages()
        
        if not allow_unknown_song:
            # we need to check that the song
            # is know by echonest or lastfm
            # otherwhise, import is rejected
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
        
        if name is None and filename is not None:
            name = filename
        
        if name is None:
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

        self._log('echonest id = %s, lastfm_id = %s, musicbrainz_id = %s' % (echonest_id, lastfm_id, musicbrainz_id))
        
        # avoid stale data        
        flush_transaction()
        
        sm = None
        if song_metadata_id:
            try:
                sm = SongMetadata.objects.get(id=song_metadata_id)
                self._log(_("song metadata given and found : %s") % (song_metadata_id))
            except SongMetadata.DoesNotExist:
                self._log(_("song metadata does not exists : %s") % (song_metadata_id))

                        
        # create artist with info from echonest and lastfm
        self._log(_('looking for artist'))
        artist = self._get_or_create_artist(metadata)
        # create album if found on lastfm
        self._log(_('looking for album'))
        album = self._get_or_create_album(metadata)
        
        # create yasound song
        self._log(_('looking for song'))
        found = self._find_server_version(metadata)
        if found:
            song = found
            provided_fingerprint = self._find_lastfm_fingerprintid(metadata)
            self._log("Song already existing in database (id=%s), replacing with provided version" % (song.id))
            song.replace(filepath, provided_fingerprint)
            
            if not sm:
                self._log('creating songmetadata: name=%s, artist_name=%s, album_name=%s, yasound_song_id=%s' % (name, artist_name, album_name, song.id))
                candidates = SongMetadata.objects.filter(name=name, artist_name=artist_name, album_name=album_name, yasound_song_id=song.id)
                if candidates.count() > 0:
                    sm = candidates[0]
                else:
                    sm = SongMetadata.objects.create(name=name, artist_name=artist_name, album_name=album_name, yasound_song_id=song.id)
                self._log('creating songmetadata: done')
        else:
            if not sm:      
                # create new song metadata
                sm = SongMetadata.objects.create(name=name, artist_name=artist_name, album_name=album_name)

            
            # generate filename and save mp3 to disk
            self._log(_('generating filename'))
            filename, mp3_path = self._generate_filename_and_path_for_song()
            try:
                os.makedirs(os.path.dirname(mp3_path))
            except OSError as e:
                if e.errno == errno.EEXIST:
                    pass
                else: raise
            
            owner_id = self._get_owner_id(metadata=metadata, echonest_id=echonest_id, lastfm_id=lastfm_id)
            
            lastfm_fingerprint_id = self._find_lastfm_fingerprintid(metadata)
            
            # create song object
            self._log(_('creating YasoundSong'))
            song = YasoundSong(artist=artist,
                               album=album,
                               echonest_id=echonest_id,
                               lastfm_fingerprint_id=lastfm_fingerprint_id,
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
                               tempo=Decimal(str(tempo)),
                               tonality_mode=tonality_mode,
                               tonality_key=tonality_key,
                               fingerprint=fingerprint,
                               fingerprint_hash=fingerprint_hash,
                               echoprint_version=echoprint_version,
                               publish_at=None,
                               published=False,
                               locked=False,
                               owner_id=owner_id,
                               quality=quality)
            song.save()
            self._log(_('YasoundSong generated, id = %s') % (song.id))
            
            self._log(_('generating file data'))

            shutil.copy(filepath, mp3_path)
            self._log("copied %s to %s" % (filepath, mp3_path))
                
            # generate 64kb preview
            self._log(_('generating preview'))
            song.generate_preview()
            self._log("generated mp3 preview file : %s" % (song.get_song_preview_path()))
            
            song.filesize = os.path.getsize(mp3_path)
            song.save()
            
        # assign genre
        self._log('assigning genres')
        genres = metadata.get('genres')
        if genres:
            for genre in genres:
                genre_canonical = get_simplified_name(genre)
                yasound_genre, created = YasoundGenre.objects.get_or_create(name_canonical=genre_canonical, defaults={'name': genre})
                if created:
                    self._log("creating genre: %s" % (genre))
                _song_genre, created = YasoundSongGenre.objects.get_or_create(song=song, genre=yasound_genre)
                if created:
                    self._log("genre %s associated with song %s" % (genre, song))
        self._log('assigning genres: done')
                    
        
        # assign song id to metadata
        self._log('association between YasoundSong and SongMetadata')
        sm.yasound_song_id = song.id
        sm.save()
        self._log(_('Association between YasoundSong and SongMetadata done'))
        
        # creating song instance if needed
        self._create_song_instance(sm, metadata)

        # avoid stale data        
        flush_transaction()
        
        self._log(_('Building mongodb index'))
        build_mongodb_index()
        return sm, self.get_messages()
    
    def find_song_cover_data(self, filename):
        """
        return data, extension
        """
        from mutagen import File

        data = None
        extension = None

        try:
            file = File(filename)
        except:
            logger.error(u'error while opening: %s' % (filename))
            return data, extension

        if not file or not file.tags:
            return data, extension
        
        try:
            pics = file.tags.getall('APIC')
        except:
            pics = []
        for pic in pics:
            mime = pic.mime
            extension = None
            
            if mime == 'image/jpeg':
                extension = '.jpg'
            elif mime == 'image/png':
                extension = '.png'
            # TODO : support '-->' for uri            
            if not extension:
                continue
            
            data = pic.data
            if not data:
                continue        
            break
        
        if 'covr' in file.tags:
            for pic in file.tags['covr']:
                if 'PNG' in pic:
                    return pic, '.png'
                else:
                    return pic, '.jpg'
            
        return data, extension
        
        
    def extract_song_cover(self, yasound_song, filepath=None):
        logger.info("extracting song cover from %d (%s) : start" % (yasound_song.id, yasound_song))
        
        if yasound_song.cover_filename:
            logger.info("song %d (%s) has a cover" % (yasound_song.id, yasound_song))
            return

        if filepath:
            mp3 = filepath
        else:
            mp3 = os.path.join(settings.SONGS_ROOT, convert_filename_to_filepath(yasound_song.filename))

        data, extension = self.find_song_cover_data(mp3)
        if data is not None and extension is not None:
            filename, path = self._generate_filename_and_path_for_song_cover(extension)
            try:
                os.makedirs(os.path.dirname(path))
            except OSError as e:
                if e.errno == errno.EEXIST:
                    pass
                else: raise
            
            with open(path, 'wb') as img:
                img.write(data) 
                yasound_song.cover_filename = filename
                logger.info('ok, saved in %s' % path)
                yasound_song.save()            
        
        logger.info("extracting song cover from %d (%s) : done" % (yasound_song.id, yasound_song))


def import_song(filepath, metadata, convert, allow_unknown_song=False, song_metadata_id=None): 
    """
    import song and extract cover
    """   
    importer = SongImporter()
    sm, messages = importer.import_song(filepath, metadata, convert, allow_unknown_song, song_metadata_id=song_metadata_id) 
    if sm and sm.yasound_song_id:
        try:
            yasound_song = YasoundSong.objects.get(id=sm.yasound_song_id)
            importer.extract_song_cover(yasound_song, filepath)
        except:
            pass
        
    return sm, messages
    
def generate_default_filename(metadata):
    now = datetime.datetime.now()
    now_str = now.strftime('%Y-%m-%d-%H:%M')
    filename = now_str
    if metadata:
        radio_id = metadata.get('radio_id')
        if radio_id:
            radio = Radio.objects.get(id=radio_id)
            filename = u'%s-%s' % (radio, now_str)  
    return filename

    
def extract_song_cover(yasound_song):
    importer = SongImporter()
    return importer.extract_song_cover(yasound_song)

def parse_itunes_line(line):
    line = line.strip()
    items = line.split('\t')
    name, album, artist = '', '', ''
    try:
        name = items[0].strip()
        artist = items[3].strip()
        album = items[4].strip()
    except:
        pass
    return name, album, artist
    
def import_from_string(song_name, album_name, artist_name, playlist):
    song_name_simplified = get_simplified_name(song_name)
    album_name_simplified = get_simplified_name(album_name)
    artist_name_simplified = get_simplified_name(artist_name)
    song_instance = None
    hash_name = md5.new()
    hash_name.update(song_name_simplified)
    hash_name.update(album_name_simplified)
    hash_name.update(artist_name_simplified)
    hash_name_hex = hash_name.hexdigest()
    
    raw = SongMetadata.objects.raw("SELECT * from yabase_songmetadata WHERE hash_name=%s AND name=%s AND artist_name=%s AND album_name=%s",
                                   [hash_name_hex,
                                    song_name,
                                    artist_name,
                                    album_name])
    if raw and len(list(raw)) > 0:
        metadata = list(raw)[0]
    else:
        metadata = SongMetadata.objects.create(name=song_name,
                                               artist_name=artist_name,
                                               album_name=album_name,
                                               hash_name=hash_name_hex)
        
    raw = SongInstance.objects.raw('SELECT * FROM yabase_songinstance WHERE playlist_id=%s and metadata_id=%s',
                                   [playlist.id,
                                    metadata.id])
    if raw and len(list(raw)) > 0:
        song_instance = list(raw)[0]
    else:
        song_instance = SongInstance.objects.create(playlist=playlist, metadata=metadata, frequency=0.5, enabled=True)

    if metadata.yasound_song_id is None:
        mongo_doc = YasoundSong.objects.find_fuzzy(song_name_simplified, 
                                                   album_name_simplified, 
                                                   artist_name_simplified)
        if mongo_doc is not None:
            SongMetadata.objects.filter(id=metadata.id).update(yasound_song_id = mongo_doc.get('db_id'))

    return song_instance 
    