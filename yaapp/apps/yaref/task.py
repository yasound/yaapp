from celery.task import task
from yabase.models import SongMetadata
from yaref.models import YasoundSong
from yaref.mongo import SongAdditionalInfosManager, JobManager
import logging
from tempfile import mkdtemp
import utils as yaref_utils
import shutil
import random

from django.conf import settings

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


@task(ignore_result=True)
def async_generate_low_quality(yasound_song_id):
    song = YasoundSong.objects.get(id=yasound_song_id)
    song.generate_low_quality()


@task(rate_limit='8/s', ignore_result=True, max_retries=2000)
def async_convert_song(yasound_song_id, dry=False, primary=False, exclude_primary=False):
    jm = JobManager()
    convert_jobs_count = jm.get(settings.CONVERT_JOBS_COUNT_KEY, 0)

    logger.info('convert_jobs_count = %d' % (convert_jobs_count))
    if convert_jobs_count > 6:
        countdown = random.randrange(20, 180)
        logger.info('too much job, retrying in %d seconds' % (countdown))
        raise async_convert_song.retry(countdown=countdown)

    logger.info('converting song %s, dry=%s, primary=%s, exclude_primary=%s' % (yasound_song_id, dry, primary, exclude_primary))
    song = YasoundSong.objects.get(id=yasound_song_id)

    jm.inc(settings.CONVERT_JOBS_COUNT_KEY, 1)

    manager = SongAdditionalInfosManager()
    doc = manager.information(yasound_song_id)
    if doc is None:
        doc = {
            'db_id': song.id
        }
    conversion_status = doc.get('conversion_status')
    if conversion_status is None:
        conversion_status = {
            'converted': False,
            'in_progress': False,
            'high_quality_finished': False,
            'low_quality_finished': False,
            'preview_finished': False
        }
    information = {
        'conversion_status': conversion_status
    }
    manager.add_information(song.id, information)

    if dry:
        jm.inc(settings.CONVERT_JOBS_COUNT_KEY, -1)
        return

    if conversion_status.get('in_progress'):
        logger.info('song conversion in progress, giving up')
        jm.inc(settings.CONVERT_JOBS_COUNT_KEY, -1)
        return

    conversion_status['in_progress'] = True
    manager.add_information(song.id, information)

    # convert hq
    if not exclude_primary:
        if not conversion_status.get('high_quality_finished'):
            logger.info('converting high quality file %s' % (yasound_song_id))
            source = song.get_song_path()
            directory = mkdtemp(dir=settings.TEMP_DIRECTORY)
            destination = u'%s/converted.mp3' % (directory)

            res = yaref_utils.convert_to_mp3(settings.FFMPEG_BIN, settings.FFMPEG_CONVERT_HIGH_QUALITY_OPTIONS, source, destination)
            if not res:
                logger.error('cannot convert %s to %s' % (source, destination))
                conversion_status['in_progress'] = False
                manager.add_information(song.id, information)
                jm.inc(settings.CONVERT_JOBS_COUNT_KEY, -1)
                return

            hq_destination = song.get_song_hq_path()
            try:
                shutil.copy(destination, hq_destination)
            except:
                logger.error('cannot copy %s to %s' % (destination, hq_destination))

            shutil.rmtree(directory)

            conversion_status['high_quality_finished'] = True
            manager.add_information(song.id, information)
        else:
            logger.info('hq conversion already done for %s' % (yasound_song_id))

    if not primary:
        if not conversion_status.get('low_quality_finished'):
            # convert lq
            logger.info('converting low quality file %s' % (yasound_song_id))
            source = song.get_song_path()
            directory = mkdtemp(dir=settings.TEMP_DIRECTORY)
            destination = u'%s/converted.mp3' % (directory)

            res = yaref_utils.convert_to_mp3(settings.FFMPEG_BIN, settings.FFMPEG_CONVERT_LOW_QUALITY_OPTIONS, source, destination)
            if not res:
                logger.error('cannot convert %s to %s' % (source, destination))
                conversion_status['in_progress'] = False
                manager.add_information(song.id, information)
                jm.inc(settings.CONVERT_JOBS_COUNT_KEY, -1)
                return

            lq_destination = song.get_song_lq_path()
            try:
                shutil.copy(destination, lq_destination)
            except:
                logger.error('cannot copy %s to %s' % (destination, lq_destination))
            shutil.rmtree(directory)

            conversion_status['low_quality_finished'] = True
            manager.add_information(song.id, information)
        else:
            logger.info('lq conversion already done for %s' % (yasound_song_id))

    conversion_status['in_progress'] = False
    manager.add_information(song.id, information)

    jm.inc(settings.CONVERT_JOBS_COUNT_KEY, -1)
    logger.info('conversion done for %s (%s)' % (yasound_song_id, song.get_song_hq_path()))
