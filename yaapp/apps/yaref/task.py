from celery.task import task
from yabase.models import SongMetadata
from yaref.models import YasoundSong
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
            SongMetadata.objects.create(name=name,
                                        artist_name=artist_name,
                                        album_name=album_name,
                                        yasound_song_id=yasound_song_id)