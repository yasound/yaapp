from models import YasoundSong
from yasearch.utils import get_simplified_name

def generate_yasound_song(name, album, artist):
    song = YasoundSong(name=name,
                name_simplified=get_simplified_name(name),
                artist_name=artist,
                artist_name_simplified=get_simplified_name(artist),
                album_name=album,
                album_name_simplified=get_simplified_name(album),
                filename='filename',
                duration=10,
                filesize=10)
    song.save()
    return song