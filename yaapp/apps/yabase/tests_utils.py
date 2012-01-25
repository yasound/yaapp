from models import SongInstance, Playlist, Radio, NextSong, SongMetadata

import datetime

def generate_playlist(name='playlist1', song_count=30):
    playlist = Playlist(name=name, source=name)
    playlist.save()
    for i in range(1, song_count+1):
        sm = SongMetadata(artist_name='artist%d' % i,
                          album_name='album%d' % i,
                          name='name%d' % i)
        sm.save()
        si = SongInstance(playlist=playlist,
                          song=i,
                          metadata=sm,
                          last_play_time=datetime.datetime(2010, 01, 01, i, 0),
                          order=i)
        si.save()
    return playlist
