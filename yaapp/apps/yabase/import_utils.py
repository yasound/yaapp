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
from yabase.models import SongMetadata
from yaref.models import YasoundSong, YasoundArtist, YasoundAlbum, YasoundGenre, \
    YasoundSongGenre
from yaref.utils import get_simplified_name, convert_filename_to_filepath
import datetime
import hashlib
import logging
import os
import random
import requests

logger = logging.getLogger("yaapp.yabase")

def _find_echonest_id_for_artist(metadata):
    data = metadata.get('echonest_data')
    if not data:
        return None
    return data.get('artist_id')

def _find_mb_id_for_song(metadata):
    if not metadata['lastfm_data']:
        return None
    return metadata.get('mbid')

def _find_mb_id_for_artist(metadata):
    lastfm_data = metadata.get('lastfm_data')
    if not lastfm_data:
        return None
    
    artist = lastfm_data.get('artist')
    if not artist:
        return None
    
    return artist[0].get('mbid')


def _find_mb_id_for_album(metadata):
    lastfm_data = metadata.get('lastfm_data')
    if not lastfm_data:
        return None
    
    album = lastfm_data.get('album')
    if not album:
        return None
    
    return album.get('mbid')

def _find_cover_url_for_album(metadata):
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

def _find_audio_summary(metadata):
    data = metadata.get('echonest_data')
    if not data:
        return None
    return data.get('audio_summary')

def _find_audio_summary_item(metadata, item):
    audio_summary = _find_audio_summary(metadata)
    if not audio_summary:
        return None
    return audio_summary.get(item)

def _generate_filename_and_path_for_song():
    path_exists = True
    filename = None
    while path_exists:
        filename = ''.join(random.choice("01234567890abcdef") for i in xrange(9)) + '.mp3'
        path = os.path.join(settings.SONGS_ROOT, convert_filename_to_filepath(filename))
        path_exists = os.path.exists(path)
    return filename, path

def _generate_filename_and_path_for_cover(url):
    extension = url[-4:len(url)]
    path_exists = True
    filename = None
    while path_exists:
        filename = ''.join(random.choice("01234567890abcdef") for i in xrange(9)) + extension
        path = os.path.join(settings.ALBUM_COVERS_ROOT, convert_filename_to_filepath(filename))
        path_exists = os.path.exists(path)
    return filename, path

def _get_filepath_for_preview(filepath):
    name, extension = os.path.splitext(filepath)
    preview = u'%s_preview64%s' % (name, extension)
    return preview
 
def _generate_preview(source, destination):
    import subprocess as sub
    logger.info('generating preview for %s' % (source))
    args = [settings.FFMPEG_BIN, 
            '-i',
            source]
    args.extend(settings.FFMPEG_GENERATE_PREVIEW_OPTIONS.split(" "))
    args.append(destination)
    p = sub.Popen(args,stdout=sub.PIPE,stderr=sub.PIPE)
    output, errors = p.communicate()
    if len(errors) == 0:
        logger.info(errors)
        return False
    return True    
    
def _get_quality(metadata):
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
    
def _get_or_create_artist(metadata):
    echonest_id = _find_echonest_id_for_artist(metadata)
    mb_id = _find_mb_id_for_artist(metadata)
    name = metadata.get('artist')
    name_simplified = get_simplified_name(name)
    
    if not (echonest_id or mb_id or name):
        logger.info("artist info not sufficient")
        return None
    
    try:
        artist = YasoundArtist.objects.get(echonest_id=echonest_id)
    except YasoundArtist.DoesNotExist:
        logger.info("creating new artist (echonest_id=%s): %s" % (name, echonest_id))
        artist = YasoundArtist(echonest_id=echonest_id,
                               musicbrainz_id=mb_id,
                               name=name,
                               name_simplified=name_simplified)
        artist.save()
    return artist

def _get_or_create_album(metadata):
    lastfm_id = metadata.get('album_lastfm_id')
    if not lastfm_id:
        logger.info("no lastfm info about album")
        return None
    
    try:
        album = YasoundAlbum.objects.get(lastfm_id=lastfm_id)
        logger.info("album already in database")
        return album
    except YasoundAlbum.DoesNotExist:
        pass
    
    mbid = _find_mb_id_for_album(metadata)
    name = metadata.get('album')
    logger.info("creating new album: %s" % (name))
    name_simplified = get_simplified_name(name)
    cover_filename = None
    cover_url = _find_cover_url_for_album(metadata)
    if cover_url:
        # saving cover
        cover_filename, cover_path = _generate_filename_and_path_for_cover(cover_url)
        r = requests.get(cover_url)
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



def import_song(metadata, binary):
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

    logger.info("importing %s-%s-%s" % (name, album_name, artist_name))

    echonest_data = metadata.get('echonest_data')
    lastfm_data = metadata.get('lastfm_data')
    if not echonest_data and not lastfm_data:
        logger.error("no echonest and lastfm datas")
        return
    fingerprint = metadata.get('fingerprint')
    if not fingerprint:
        logger.error("no fingerprint")
        return
    fingerprint_hash = hashlib.sha1(fingerprint).hexdigest()
    
    now = datetime.datetime.today()
    
    if not name:
        logger.error("no title")
        return None
    name_simplified = get_simplified_name(name)
    artist_name_simplified = get_simplified_name(artist_name)
    album_name_simplified = get_simplified_name(album_name)
    
    duration = _find_audio_summary_item(metadata, 'duration')
    loudness = _find_audio_summary_item(metadata, 'loudness')
    danceability = _find_audio_summary_item(metadata, 'danceability')
    energy = _find_audio_summary_item(metadata, 'energy')
    tempo = _find_audio_summary_item(metadata, 'tempo')
    tonality_mode = _find_audio_summary_item(metadata, 'mode')
    tonality_key = _find_audio_summary_item(metadata, 'key')
    echoprint_version = metadata.get('echoprint_version')
    
    echonest_id = metadata.get('echonest_id')
    lastfm_id = metadata.get('lastfm_id')
    musicbrainz_id = _find_mb_id_for_song(metadata)
    duration = metadata.get('duration')
    quality = _get_quality(metadata)
    
    # first check for an existing SongMetadata
    try:
        sm = SongMetadata.objects.get(name=name, artist_name=artist_name, album_name=album_name)
        if sm.yasound_song_id:
            logger.info("song already in database")
            return None
    except SongMetadata.DoesNotExist:
        sm = SongMetadata(name=name, artist_name=artist_name, album_name=album_name)
        sm.save()

    # create artist with info from echonest and lastfm
    artist = _get_or_create_artist(metadata)
    # create album if found on lastfm
    album = _get_or_create_album(metadata)
    
    # create yasound song
    songs = YasoundSong.objects.filter(Q(echonest_id=echonest_id) | Q(lastfm_id=lastfm_id))
    if songs.count() > 0:
        song_candidate = songs[0]
        if song_candidate.echonest_id is not None or song_candidate.lastfm_id is not None:
            song = song_candidate
            logger.info("Song already existing (id=%s)" % (song.id))
    else:
        # generate filename and save binary to disk
        filename, mp3_path = _generate_filename_and_path_for_song()
        os.makedirs(os.path.dirname(mp3_path))
        destination = open(mp3_path, 'wb')
        for chunk in binary.chunks():
            destination.write(chunk)
        destination.close()  
        logger.info("generated mp3 file : %s" % (mp3_path))
    
        # generate 64kb preview
        mp3_preview_path = _get_filepath_for_preview(mp3_path)
        _generate_preview(mp3_path, mp3_preview_path)
        logger.info("generated mp3 preview file : %s" % (mp3_preview_path))
        
        # create song object
        song = YasoundSong(artist=artist,
                           album=album,
                           echonest_id=echonest_id,
                           lastfm_id=lastfm_id,
                           musicbrainz_id=musicbrainz_id,
                           filename=filename,
                           filesize=os.path.getsize(mp3_path),
                           name=name,
                           name_simplified=name_simplified,
                           artist_name=artist_name,
                           artist_name_simplified=artist_name_simplified,
                           album_name=album_name,
                           album_name_simplified=album_name_simplified,
                           duration=duration,
                           danceability=danceability,
                           loudness=loudness,
                           energy=energy,
                           tempo=tempo,
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
    # assign genre
    genres = metadata.get('genres')
    if genres:
        for genre in genres:
            genre_canonical = get_simplified_name(genre)
            yasound_genre, created = YasoundGenre.objects.get_or_create(namecanonical=genre_canonical, defaults={'name': genre})
            YasoundSongGenre.objects.get_or_create(song=song, genre=yasound_genre)
    
    
    # assign song id to metadata
    sm.yasound_song_id = song.id
    sm.save()
    return sm
    
    
    
    
    
    