from django.db import models
from django.conf import settings
from yaref.models import YasoundSong
import datetime
import csv
import os
import settings as yareport_settings
import string

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
        
def clean_string(s, allowed_characters, allow_numeric=True, to_upper=True, replace_with_space=True, char_count=None, left_justify=True):
    if to_upper:
        s = s.upper()
    
    x = ''
    for i in s:
        if i in allowed_characters:
            x += i
        elif allow_numeric and i in string.digits:
            x += i
        elif replace_with_space:
            x += ' '
            
    if char_count is not None:
        x = x[:char_count]
        if left_justify:
            x = x.ljust(char_count)
    return x
            
        
def sacem_report(destination_folder='', start_date=None, end_date=None):
    allowed_characters = string.uppercase + '().-/'
    db = settings.MONGO_DB
    radio_ids = db.reports.distinct("radio_id")
    for radio_id in radio_ids:
        query_dict = {}
        query_dict["radio_id"] = radio_id
        documents = db.reports.find(query_dict).sort('report_date', 1)    
        radio_name = documents[0]["radio_name"]
        filename = '%s_sacem_report.txt' % radio_name
        if destination_folder and destination_folder != '':
            path = os.path.join(destination_folder, filename)
        else:
            path = filename
        f = open(path, 'w')
        
        if start_date or end_date:
                query_dict["report_date"] = {}
                if start_date:
                    query_dict["report_date"]['$gte'] = start_date
                if end_date:
                    query_dict["report_date"]['$lt'] = end_date
        song_ids = db.reports.find(query_dict).distinct("yasound_song_id")
        
        s = start_date
        if not s:
            s = documents[0]['report_date']
        e = end_date
        if not e:
            e = documents[documents.count() - 1]['report_date']
            
        declarant_code = yareport_settings.sacem_declarant_identifier_short
        declarant_code = clean_string(declarant_code, allowed_characters)
        report_start_date = s.strftime('%y%m%d')
        report_end_date = e.strftime('%y%m%d')
        report_start_hour = s.time().strftime('%H')
        report_end_hour = e.time().strftime('%H')
        
                
        declarant_identifier = yareport_settings.sacem_declarant_identifier_full
        declarant_identifier = clean_string(declarant_identifier, allowed_characters, char_count=30)
        
        declarant_address_1 = yareport_settings.sacem_declarant_address_line1
        declarant_address_1 = clean_string(declarant_address_1, allowed_characters, char_count=25)
        
        declarant_address_2 = yareport_settings.sacem_declarant_address_line2
        declarant_address_2 = clean_string(declarant_address_2, allowed_characters, char_count=25)
        
        report_header = '%s %s %s %s %s %s %s %s\r\n' % (declarant_code, report_start_date, report_end_date, report_start_hour, report_end_hour, declarant_identifier, declarant_address_1, declarant_address_2)
        f.write(report_header)
        
        for song_id in song_ids:
            q = query_dict
            q["yasound_song_id"] = song_id
            song_docs = db.reports.find(q)
            count = song_docs.count()
            doc = song_docs[0]
            
            song_name = clean_string(doc['song_name'], allowed_characters, char_count=24)
            
            count = min(count, 9999) # limited to 4 digits
            count_str = '%04d' % count
            
            song_number = '1' # song number in advertisement campaign
            
            duration_seconds = doc["duration"] * count
            minutes = int(duration_seconds) / 60
            seconds = duration_seconds - (minutes * 60)
            if minutes > 9999:
                minutes = 9999
                seconds = 59
            duration_str = '%04d:%02d' % (minutes, seconds)
            
            artist = clean_string(doc['song_artist_name'], allowed_characters, char_count=24)
            composer = clean_string('', allowed_characters, char_count=24)
            arranger = clean_string('', allowed_characters, char_count=24)
            editor = clean_string('', allowed_characters, char_count=24)
            genre = clean_string('', allowed_characters, char_count=3)
            producer = clean_string('', allowed_characters, char_count=24)
            catalog_number = clean_string('', allowed_characters, char_count=20)
            bar_code = clean_string('', allowed_characters, char_count=13)
            
            report_row = '%s %s %s %s %s %s %s %s %s %s %s %s\r\n' % (song_name, count_str, song_number, duration_str, artist, composer, arranger, editor, genre, producer, catalog_number, bar_code)
            f.write(report_row)
        f.close()
    
    
    