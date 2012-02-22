import datetime
import hashlib

from yabase.models import SongMetadata
from yaref.utils import get_simplified_name

import logging
logger = logging.getLogger("yaapp.yabase")

def _find_mb_id_for_song(metadata):
    if not metadata['lastfm_data']:
        return None
    return metadata.get('mbid')

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

def import_song(metadata, binary):
    echonest_data = metadata.get('echonest_data')
    lastfm_data = metadata.get('lastfm_data')
    if not echonest_data and not lastfm_data:
        logger.log("no echonest and lastfm datas")
        return
    fingerprint = metadata.get('fingerprint')
    if not fingerprint:
        logger.log("no fingerprint")
        return
    fingerprint_hash = hashlib.sha1(fingerprint).hexdigest()
    
    
    
    now = datetime.datetime.today()
    
    name = metadata.get('title')
    artist_name = metadata.get('artist')
    album_name = metadata.get('album')
    
    if not name:
        logger.log("no title")
        return
    name_simplified = get_simplified_name(name)
    artist_name_simplified = get_simplified_name(artist_name)
    album_name_simplified = get_simplified_name(album_name)
    
    duration = _find_audio_summary_item('duration')
    loudness = _find_audio_summary_item('loudness')
    danceability = _find_audio_summary_item('danceability')
    energy = _find_audio_summary_item('energy')
    tempo = _find_audio_summary_item('tempo')
    tonality_mode = _find_audio_summary_item('mode')
    tonality_key = _find_audio_summary_item('key')
    echoprint_version = metadata.get('echoprint_version')
    
    echonest_id = metadata.get('echonest_id')
    lastfm_id = metadata.get('lastfm_id')
    musicbrainz_id = _find_mb_id_for_song(metadata)
        
    # first check for an existing SongMetadata
    try:
        sm = SongMetadata.objects.get(name=name, artist_name=artist_name, album_name=album_name)
        if sm.yasound_song_id:
            logger.log("song already in database")
            return
    except SongMetadata.DoesNotExist:
        sm = SongMetadata(name=name, artist_name=artist_name, album_name=album_name)
        sm.save()
        
    
    
    
    
    
    
    