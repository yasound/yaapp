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

    for playlist in playlists.get('data', []):
        # add link with our user database
        playlist['creator']['username'] = username
        pm.add(playlist)

    tm = TrackManager()
    for playlist in playlists.get('data', []):
        url = 'https://api.deezer.com/2.0/playlist/%s' % (playlist.get('id'))
        r = requests.get(url, params=params)
        playlist_detail = r.json
        for track in playlist_detail.get('tracks', []).get('data', []):
            # add playlist info (which is an array of id)
            ps = track.get('playlist', [])
            ps.append(playlist.get('id'))
            ps = list(set(ps))
            track['playlists'] = ps
            tm.add(track)
