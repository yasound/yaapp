from celery.task import task
from django.conf import settings
from django.contrib.auth.models import User
from models import PlaylistManager, TrackManager
import requests
import logging
logger = logging.getLogger("yaapp.yadeezer")

@task
def import_playlists_task(username, token):
    url = 'https://api.deezer.com/2.0/user/me/playlists'
    params = {
        'access_token': token
    }
    r = requests.get(url, params=params)
    playlists = r.json

    pm = PlaylistManager()

    logger.debug('received')
    logger.debug(playlists)

    for playlist in playlists.get('data'):
        playlist['creator']['username'] = username
        pm.add(playlist)

    tm = TrackManager()
    for playlist in playlists.get('data'):
        url = 'https://api.deezer.com/2.0/user/me/playlist/%s' % (playlist.get('id'))
        r = requests.get(url, params=params)
        tracks = r.json
        logger.debug('----------------')
        logger.debug('received')
        logger.debug(tracks)
        for track in tracks.get('data'):
            # add playlist info
            ps = track.get('playlist', [])
            ps.append(playlist.get('id'))
            ps = list(set(ps))
            track['playlists'] = ps

            tm.add(track)