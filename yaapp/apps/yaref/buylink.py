from django.conf import settings
import requests
import json
    
def _get_separator(track_view_url):
    index = track_view_url.find('?')
    if index == -1:
        return '?'
    else:
        return '&'

def _get_track_view_url(data):
    if 'results' in data:
        for item in data['results']:
            if 'trackViewUrl' in item:
                return item['trackViewUrl']
    return None
        
    
def _generate_buy_link(song, album, artist):
    trade_url = None
    song_sanitized = song.replace('\n', ' ')
    album_sanitized = album.replace('\n', ' ')
    artist_sanitized = artist.replace('\n', ' ')
    
    terms = u'%s %s %s' % (artist_sanitized, album_sanitized, song_sanitized)
    url_string = u'%s?term=%s&entity=musicTrack&limit=1&country=FR' % (settings.ITUNES_BASE_URL, terms)
    r = requests.get(url_string)
    
    if r.status_code != 200:
        return trade_url
    
    data = json.loads(r.content)
    track_view_url = _get_track_view_url(data)
    
    if track_view_url is None:
        return trade_url
    
    trade_url = u'%s%s%s%s' % (settings.TRADEDOUBLER_URL, 
                       track_view_url, 
                       _get_separator(track_view_url),
                       settings.TRADEDOUBLER_ID)
    
    return trade_url

def generate_buy_link(song, album, artist):
    trade_url = _generate_buy_link(song, album, artist)
    if not trade_url:
        trade_url = _generate_buy_link(song, '', artist)
    return trade_url