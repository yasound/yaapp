from celery.task import task
from yabase.models import SongMetadata
from yaref.models import YasoundSong
from yaref.mongo import SongAdditionalInfosManager
import logging
logger = logging.getLogger("yaapp.yaref")

@task(ignore_result=True)
def find_musicbrainz_id(yasound_song_id):
    logger = find_musicbrainz_id.get_logger()
    logger.info('finding musicbrainz id for song %s' % (yasound_song_id))
    song = YasoundSong.objects.get(id=yasound_song_id)
    mbid = song.find_mbid()
    if mbid is not None:
        logger.info('found: %s' % (mbid))
        YasoundSong.objects.filter(id=yasound_song_id).update(musicbrainz_id=mbid)
    else:
        logger.debug('not found')
    
@task(rate_limit='1/s', ignore_result=True)
def async_find_synonyms(yasound_song_id):
    logger = async_find_synonyms.get_logger()
    logger.info('finding synonyms for %s' % (yasound_song_id))
    song = YasoundSong.objects.get(id=yasound_song_id)
    synonyms = song.find_synonyms()
    for s in synonyms:
        name = s.get('name')
        artist_name = s.get('artist')
        album_name = s.get('album')
        
        existing_sm = SongMetadata.objects.filter(yasound_song_id=yasound_song_id,
                                                  name=name,
                                                  artist_name=artist_name,
                                                  album_name=album_name)
        if existing_sm.count() == 0:
            logger.info('creating synonym: %s - %s - %s' % (name, album_name, artist_name))
            sm = SongMetadata(name=name,
                             artist_name=artist_name,
                             album_name=album_name,
                             yasound_song_id=yasound_song_id)
            sm.calculate_hash_name(commit=True)
            

@task(rate_limit='180/s', ignore_result=True)
def async_convert_song(yasound_song_id):
    song = YasoundSong.objects.get(id=yasound_song_id)
    manager =SongAdditionalInfosManager()
    doc = manager.information(song)
    if doc is None:
        doc = {
            'db_id': song.id
        }
    conversion_status = doc.get('conversion_status')
    if conversion_status is None:
        conversion_status = {
            'converted': False,
            'high_quality_finished': False,
            'low_quality_finished': False,
            'preview_finished': False
        }
        information = {
            'conversion_status': conversion_status
        }
        manager.add_information(song.id, information)
        