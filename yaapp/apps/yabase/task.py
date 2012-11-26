from celery.task import task
from django.contrib.auth.models import User
from django.db import transaction
from models import Playlist, SongInstance, update_leaderboard, RadioUser
from shutil import rmtree
from yabase.import_utils import parse_itunes_line, import_from_string, \
    fast_import
from yacore.database import flush_transaction
from yaref.models import YasoundSong
import import_utils
import logging
import os
import signals as yabase_signals
import time
import zlib
import datetime
from yabase import settings as yabase_settings
logger = logging.getLogger("yaapp.yabase")
from yacore.binary import BinaryData
from django.conf import settings
from yahistory.models import ProgrammingHistory


@task(ignore_result=True)
def leaderboard_update_task():
    logger.info('leaderboard_update_task started')
    flush_transaction()
    update_leaderboard()
    flush_transaction()
    logger.info('leaderboard_update_task finished')


@transaction.commit_on_success
def process_playlists_exec(radio, content_compressed, task=None):
    logger.info("decompress playlist for radio %d" % (radio.id))

    try:
        content_uncompressed = zlib.decompress(content_compressed)
    except Exception, e:
        logger.error("Cannot handle content_compressed: %s" % (unicode(e)))
        return

    logger.info('*** process_playlists ***')

    start = time.time()

    pm = ProgrammingHistory()
    event = pm.generate_event(event_type=ProgrammingHistory.PTYPE_UPLOAD_PLAYLIST,
                              user=radio.creator,
                              radio=radio,
                              status=ProgrammingHistory.STATUS_PENDING)

    PLAYLIST_TAG = 'LIST'
    ARTIST_TAG = 'ARTS'
    ALBUM_TAG = 'ALBM'
    SONG_TAG = 'SONG'
    REMOVE_PLAYLIST = 'REMV'
    REMOTE_PLAYLIST = 'RLST'
    UUID_TAG = 'UUID'

    artist_name = None
    album_name = None

    count = 0
    found = 0
    notfound = 0

    # avoid stale data
    flush_transaction()

    # create defaut playlist
    playlist, _created = radio.get_or_create_default_playlist()

    # let's play with content
    data = BinaryData(content_uncompressed)
    data_len = float(len(data.data))

    remaining_songs = []

    while not data.is_done():
        tag = data.get_tag()

        if task:
            progress = float(data.offset) / data_len
            task.update_state(state="PENDING", meta={"progress": "%.2f" % progress})

        if tag == UUID_TAG:
            _uuid = data.get_string()
        elif tag == PLAYLIST_TAG:
            _device_playlist_name = data.get_string()
        elif tag == ALBUM_TAG:
            album_name = data.get_string()
        elif tag == ARTIST_TAG:
            artist_name = data.get_string()
        elif tag == SONG_TAG:
            _order = data.get_int32()
            song_name = data.get_string()

            details = {
                'name': song_name,
                'artist': album_name,
                'album': artist_name,
            }

            creator = radio.creator
            if creator is not None and creator.is_superuser:
                song_instance = fast_import(song_name=song_name,
                                            album_name=album_name,
                                            artist_name=artist_name,
                                            playlist=playlist)

                if not song_instance:
                    remaining_songs.append({
                        'song_name': song_name,
                        'album_name': album_name,
                        'artist_name': artist_name,
                    })
            else:
                song_instance = import_from_string(song_name=song_name,
                                                   album_name=album_name,
                                                   artist_name=artist_name,
                                                   playlist=playlist,
                                                   event=event)
            if song_instance:
                found += 1
            else:
                notfound += 1

        elif tag == REMOVE_PLAYLIST:
            _device_playlist_name = data.get_string()
            _device_source = data.get_string()
        elif tag == REMOTE_PLAYLIST:
            _device_playlist_name = data.get_string()
            _device_source = data.get_string()

    logger.info('playlist parsing finished, computing ready flag')
    songs_ok = SongInstance.objects.filter(playlist__in=radio.playlists.all(), metadata__yasound_song_id__gt=0)[:1]
    if len(songs_ok) > 0:
        logger.info('existing songs founds, activating radio')
        radio.ready = True
        radio.save()
        logger.info('filling next songs queue: start')
        radio.fill_next_songs_queue()
        logger.info('filling next songs queue: finished')
    else:
        logger.info('no existing songs found')

    elapsed = time.time() - start
    logger.info('found: %d - not found: %d - total: %d in in %s seconds' % (found, notfound, count, elapsed))

    pm.finished(event)

    if len(remaining_songs) > 0:
        logger.info('launching task for remaining songs')
        async_find_remaining_songs.delay(remaining_songs, playlist.id)
    return found, notfound


@task
def async_find_remaining_songs(songs, playlist_id):
    playlist = Playlist.objects.get(id=playlist_id)
    for song in songs:
        song_name = song.get('song_name')
        artist_name = song.get('artist_name')
        album_name = song.get('album_name')

        import_from_string(song_name=song_name,
                           album_name=album_name,
                           artist_name=artist_name,
                           playlist=playlist)
    radio = playlist.radio
    if radio.ready:
        return

    songs_ok = SongInstance.objects.filter(playlist__in=radio.playlists.all(), metadata__yasound_song_id__gt=0)[:1]
    if len(songs_ok) > 0:
        radio.ready = True
        radio.save()
        radio.fill_next_songs_queue()


@task
def process_playlists(radio, content_compressed):
    return process_playlists_exec(radio, content_compressed, task=process_playlists)


def process_need_sync_songs_exec():
    """
    try to match all needed sync songs with the yasound songs
    """
    songs = SongInstance.objects.filter(need_sync=True, metadata__yasound_song_id__isnull=True).select_related()
    for song in songs:
        metadata = song.metadata
        if not metadata:
            continue
        name = metadata.name
        album = metadata.album_name
        artist = metadata.artist_name
        mongo_doc = YasoundSong.objects.find_fuzzy(name, album, artist)
        if mongo_doc:
            metadata.yasound_song_id = mongo_doc['db_id']
            metadata.save()
            song.need_sync = False
            song.save()


@task
def process_need_sync_songs():
    return process_need_sync_songs_exec()


@task
def process_upload_song(filepath, metadata=None, convert=True, song_id=None, allow_unknown_song=False):
    logger.debug('processing %s' % (filepath))

    sm, _messages = import_utils.import_song(filepath=filepath, metadata=metadata, convert=convert, allow_unknown_song=allow_unknown_song)
    if song_id and sm:
        SongInstance.objects.filter(id=song_id).update(metadata=sm)
    path = os.path.dirname(filepath)
    logger.debug('deleting %s' % (path))
    rmtree(path)


@task
def generate_low_quality(yasound_song_id):
    yasound_song = YasoundSong.objects.get(id=yasound_song_id)
    yasound_song.generate_low_quality()


@task
def extract_song_cover(yasound_song_id):
    yasound_song = YasoundSong.objects.get(id=yasound_song_id)
    import_utils.extract_song_cover(yasound_song)


@task(ignore_result=True, rate_limit='10/s')
def async_dispatch_user_started_listening_song(radio, song):
    """
    Generate user_started_listening_song signals

    """
    rus = RadioUser.objects.filter(radio=radio, listening=True).select_related()
    for ru in rus:
        yabase_signals.user_started_listening_song.send(sender=ru.radio,
                                                        radio=ru.radio,
                                                        user=ru.user,
                                                        song=song)


@task(ignore_result=True)
def async_radio_broadcast_message(radio, message):
    recipients = User.objects.filter(radiouser__radio=radio, radiouser__favorite=True)
    logger.debug('async_radio_broadcast_message: radio=%s, message=%s' % (radio.id, unicode(message)))
    for recipient in recipients:
        recipient.get_profile().send_message(sender=radio.creator, radio=radio, message=message)


@task(ignore_result=True)
def async_import_from_itunes(radio, data):
    pm = ProgrammingHistory()
    event = pm.generate_event(event_type=ProgrammingHistory.PTYPE_IMPORT_FROM_ITUNES,
                              user=radio.creator,
                              radio=radio,
                              status=ProgrammingHistory.STATUS_PENDING)

    success = 0
    failure = 0
    yabase_signals.new_animator_activity.send(sender=radio,
                                              user=radio.creator,
                                              radio=radio,
                                              atype=yabase_settings.ANIMATOR_TYPE_IMPORT_ITUNES)

    lines = data.split('\n')
    for line in lines:
        name, album, artist = parse_itunes_line(line)
        logger.info('name=%s, album=%s, artist=%s' % (unicode(name), unicode(album), unicode(artist)))
        if len(name) > 0:
            playlist, _created = radio.get_or_create_default_playlist()
            song_instance = import_from_string(name, album, artist, playlist)

            data = {
                'artist': artist,
                'name': name,
                'album': album
            }
            if song_instance.metadata.yasound_song_id is not None:
                data['status'] = ProgrammingHistory.STATUS_SUCCESS
                success += 1
            else:
                data['status'] = ProgrammingHistory.STATUS_FAILED
                failure += 1

            pm.add_details(event, data)

    data = {
        'success': success,
        'failure': failure
    }

    event['status'] = ProgrammingHistory.STATUS_FINISHED
    event['data'] = data
    pm.update_event(event)


@task
def delete_radios_definitively():
    return  # JBL : do not delete radios right now
    from models import Radio
    today = datetime.datetime.today()
    expiration_date = today - datetime.timedelta(days=settings.RADIO_DELETE_DAYS)
    radios = Radio.objects.filter(deleted=True, updated__lt=expiration_date)
    for radio in radios:
        radio.delete()


@task(ignore_result=True)
def async_song_played(radio_uuid, songinstance_id):
    from models import Radio, SongInstance
    radio = Radio.objects.get(uuid=radio_uuid)
    song_instance = SongInstance.objects.get(id=songinstance_id)
    if song_instance.metadata is not None:
        logger.info('song_played: %s - %s - %s' % (song_instance.metadata.artist_name, song_instance.metadata.album_name, song_instance.metadata.name))
    radio.song_starts_playing(song_instance)
    logger.info('song_played: ok')


@task(ignore_result=True)
def async_songs_started(data):
    logger.info('async_songs_started: %d' % (len(data)))
    from models import Radio, SongInstance
    for i in data:
        if len(i) != 3:
            logger.info('async_songs_started wrong data format')
            return
        radio_uuid = i[0]
        songinstance_id = i[1]
        play_date = datetime.datetime.strptime(i[2], "%Y-%m-%dT%H:%M:%S.%f")
        song_instance = SongInstance.objects.select_related().get(id=songinstance_id)
        song_instance.playlist.radio.song_starts_playing(song_instance, play_date)
    logger.info('async_songs_started finished: %d' % (len(data)))
