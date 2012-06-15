from celery.task import task
from yaref.models import YasoundSong
import logging
logger = logging.getLogger("yaapp.yaref")

@task(ignore_result=True)
def find_musicbrainz_id(yasound_song_id):
    logger.debug('finding musicbrainz id for song %s' % (yasound_song_id))
    song = YasoundSong.objects.get(id=yasound_song_id)
    mbid = song.find_mbid()
    if mbid is not None:
        logger.debug('found: %s' % (mbid))
        YasoundSong.objects.filter(id=yasound_song_id).update(musicbrainz_id=mbid)
    else:
        logger.debug('not found')
    