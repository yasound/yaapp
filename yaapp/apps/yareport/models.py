from django.db import models
from django.conf import settings
from yaref.models import YasoundSong
import datetime
import csv
import os

def report_song(radio, song_instance):
    db = settings.MONGO_DB
    
    try:
        yasound_song = YasoundSong.objects.get(id=song_instance.metadata.yasound_song_id)
    except YasoundSong.DoesNotExist:
        print 'YasoundSong %d does not exist' % song_instance.metadata.yasound_song_id
        return

    doc = {
           "radio_id": radio.id,
           "radio_name": radio.name,
           "yasound_song_id": yasound_song.id,
           "song_name": yasound_song.name,
           "song_artist_name": yasound_song.artist_name,
           "song_album_name": yasound_song.album_name,
           "duration": yasound_song.duration,
           "report_date": datetime.datetime.now()
        } 
    db.reports.insert(doc)
    
def print_reports():
    db = settings.MONGO_DB
    i = 0
    for report in db.reports.find():
        print '%d %s (%d)  : %s - %s - %s (%d)  %d seconds' % (i, report["radio_name"], report["radio_id"], report["song_artist_name"], report["song_album_name"], report["song_name"], report["yasound_song_id"], report["duration"])
        i += 1 
    
    
    
    

def scpp_report(destination_folder='', start_date=None, end_date=None):
    db = settings.MONGO_DB

    radio_ids = db.reports.distinct("radio_id")
    for radio_id in radio_ids:
        query_dict = {}
        query_dict["radio_id"] = radio_id
        documents = db.reports.find(query_dict)        
        radio_name = documents[0]["radio_name"]
        filename = '%s_scpp_report.csv' % radio_name
        if destination_folder and destination_folder != '':
            path = os.path.join(destination_folder, filename)
        else:
            path = filename
        f = open(path, 'w')
        csv_writer = csv.writer(f)
        
        if start_date and end_date:
                query_dict["report_date"] = {"$gte": start_date, "$lt": end_date}
        song_ids = db.reports.find(query_dict).distinct("yasound_song_id")
        for song_id in song_ids:
            q = query_dict
            q["yasound_song_id"] = song_id
            song_docs = db.reports.find(q)
            count = song_docs.count()
            doc = song_docs[0]
            
            duration_seconds = doc["duration"]
            hours = int(duration_seconds / 3600)
            duration_seconds -= hours * 3600
            minutes = int(duration_seconds / 60)
            duration_seconds -= minutes * 60
            seconds = duration_seconds
            if hours > 0:
                duration_str = '%d:%02d:%02d' % (hours, minutes, seconds)
            else:
                duration_str = '%d:%02d' % (minutes, seconds)
            
            
            data = []
            data.append(doc["song_name"])           # Titre du Phonogramme
            data.append(duration_str)               # Duree repoduite
            data.append('')                         # Interpete Prenom
            data.append(doc["song_artist_name"])    # Interpete Nom
            data.append('')                         # Compositeur (Pour le classique)
            data.append('')                         # Marque ou producteur
            data.append('')                         # Code barre du support commercia
            data.append(count)                      # Nombre de reproductions ou de passage
            
            csv_writer.writerow(data)
        f.close()
    