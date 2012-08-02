import logging
from yabase.models import Radio, SongInstance
from yaref.models import YasoundSong
import random
from models import build_scpp_report_file
   
   
def build_yasound_2011_report_docs(radio=None):
    logger = logging.getLogger("yaapp.yareport")
    nb_days = 120
    nb_songs_played_per_day = 20
    nb_songs_played = nb_days * nb_songs_played_per_day
    
    if radio is None:
        try:
            radio = Radio.objects.get(id=119)
        except:
            logger.info('build_yasound_2011_report: no radio')
            return None
    songs = SongInstance.objects.filter(playlist__radio=radio, metadata__yasound_song_id__gt=0)
    songs_count = songs.count()
    logger.info('build_yasound_2011_report: %d songs' % songs_count)
    
    song_docs_map = {}
    random.seed()
    for i in range(nb_songs_played):
        rand_index = random.randrange(songs_count)
        yasound_song_id = songs[rand_index].metadata.yasound_song_id
        yasound_song = YasoundSong.objects.get(id=yasound_song_id)
        if not song_docs_map.has_key(yasound_song_id):
            doc = {
                   "radio_id": radio.id,
                   "radio_name": radio.name,
                   "yasound_song_id": yasound_song.id,
                   "song_name": yasound_song.name,
                   "song_artist_name": yasound_song.artist_name,
                   "song_album_name": yasound_song.album_name,
                   "duration": yasound_song.duration,
                   "count": 0
                } 
            song_docs_map[yasound_song_id] = doc
        song_docs_map[yasound_song_id]['count'] += 1
    
    return song_docs_map.values()


def build_yasound_2011_scpp_report_file(destination_folder='', radio=None):
    song_report_docs = build_yasound_2011_report_docs(radio)
    build_scpp_report_file(song_report_docs, destination_folder)
 
        
    
    