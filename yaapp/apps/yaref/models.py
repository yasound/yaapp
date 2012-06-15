"""
Contains models related to yasound database (ie all the songs)
"""
from django.db import models
from django.conf import settings
from fuzzywuzzy import fuzz
import yasearch.indexer as yasearch_indexer
import yasearch.search as yasearch_search
import logging
from time import time
import utils as yaref_utils
import yasearch.utils as yasearch_utils
import string
import requests
import json
logger = logging.getLogger("yaapp.yaref")

import django.db.models.options as options
from sorl.thumbnail import get_thumbnail
from django.core.files import File
from django.db.models import Q
import buylink
import os
from uploader import lastfm

if not 'db_name' in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('db_name',)    

class YasoundArtist(models.Model):
    echonest_id = models.CharField(unique=True, max_length=20)
    lastfm_id = models.CharField(max_length=20, blank=True, null=True)
    musicbrainz_id = models.CharField(max_length=36, blank=True, null=True)
    name = models.CharField(max_length=255)
    
    name_simplified = models.CharField(max_length=255)
    comment = models.TextField(null=True, blank=True)
        
    class Meta:
        db_table = u'yasound_artist'
        db_name = u'yasound'
    def __unicode__(self):
        return self.name

class YasoundAlbum(models.Model):
    lastfm_id = models.CharField(unique=True, max_length=20, null=True, blank=True)
    musicbrainz_id = models.CharField(max_length=36, blank=True, null=True)
    name = models.CharField(max_length=255)
    name_simplified = models.CharField(max_length=255)
    cover_filename = models.CharField(max_length=45, null=True, blank=True)
    
    @property
    def cover_url(self):
        if not self.cover_filename:
            return None
        short_url = '%s%s' % (settings.ALBUM_COVER_SHORT_URL,
                         yaref_utils.convert_filename_to_filepath(self.cover_filename))
        try:
            return get_thumbnail(short_url, '256x256', crop='center').url
        except:
            return None
    
    class Meta:
        db_table = u'yasound_album'
        db_name = u'yasound'
    def __unicode__(self):
        return self.name

class YasoundGenre(models.Model):
    name = models.CharField(max_length=45)
    name_canonical = models.CharField(unique=True, max_length=45)
    class Meta:
        db_table = u'yasound_genre'
        db_name = u'yasound'
    def __unicode__(self):
        return self.name

class YasoundSongManager(models.Manager):
    
    _max_query = 0
    _max_song = None
    
    def test_fuzzy(self, limit=5):
#        from yaref.models import *;YasoundSong.objects.test_fuzzy()
        import random
        from time import time
        count = 100
        random_ids = random.sample(xrange(1600000), count)
        artist_records = list(YasoundSong.objects.filter(id__in=random_ids).all())
        
        found = 0
        errors = 0
        start = time()
        for i, artist in enumerate(artist_records):
            res = self.find_fuzzy(artist.name,  artist.album_name, artist.artist_name, limit=limit) 
            if res:
                found +=1
                if res["db_id"] != artist.id:
                    if res["name"] != artist.name or res["artist"] != artist.artist_name or res["album"] != artist.album_name:
                        logger.debug("** error : %d instead of %d" % (res['db_id'], artist.id))
                        logger.debug("** wrong = %s|%s|%s" % (res["name"],res["album"],res["artist"]))
                        logger.debug("** real  = %s|%s|%s" % (artist.name,artist.album_name,artist.artist_name))
                        errors += 1
                        found -= 1
        elapsed = time() - start
        logger.debug('Complete search took ' + str(elapsed) + ' seconds')
        logger.debug('Mean : ' + str(elapsed/count) + ' seconds')
        logger.debug('Found : %d/%d (%d%%), errors = %d (%d%%)' % (found, count, 100*found/count, errors, 100*errors/count))
        if self._max_song:
            song = self.get(id=self._max_song['db_id'])
            logger.debug('slowest song : %d:%s|%s|%s (%f)' % (song.id, 
                                                              song.name, 
                                                              song.album_name, 
                                                              song.artist_name, 
                                                              self._max_query))
                     
    def last_indexed(self):
        doc = yasearch_indexer.get_last_song_doc()
        if doc and doc.count() > 0:
            return self.get(id=doc[0]['db_id'])
        return None
    
    def _check_candidates(self, songs, name, album, artist):
        best_ratio = 0
        best_song = None
        for song in songs:
            ratio_song, ratio_album, ratio_artist = 0, 0, 0

            if name is not None and song["name"] is not None:
                ratio_song = fuzz.token_sort_ratio(name, song["name"])
                
            if album is not None and song["album"] is not None:
                ratio_album = fuzz.token_sort_ratio(album, song["album"])

            if artist is not None and song["artist"] is not None:
                ratio_artist = fuzz.token_sort_ratio(artist, song["artist"])
            ratio = ratio_song + ratio_album / 4 + ratio_artist / 4

            if ratio >= best_ratio and ratio > 50:
                best_ratio = ratio
                best_song = song
        return best_song, best_ratio
    
    def find_fuzzy(self, name, album, artist, limit=5):
        from time import time
        start = time()
        songs = yasearch_search.find_song(name, album, artist, remove_common_words=True)
        song, ratio = self._check_candidates(songs, name, album, artist)
        elapsed = time() - start
        if not song:
            logger.debug('find fuzzy: %s|%s|%s : FAILED in %s seconds' % (name, album, artist, str(elapsed)))
        else:
            logger.debug('find fuzzy: %s|%s|%s : OK in %s seconds' % (name, album, artist, str(elapsed)))
        if elapsed > self._max_query:
            self._max_query = elapsed
            self._max_song = song
        return song
    
    def search_fuzzy(self, search_text, limit=25, exclude_song_ids=[]):
        print 'search fuzzy "%s"' % search_text
        songs = yasearch_search.search_song(search_text, remove_common_words=True, exclude_ids=exclude_song_ids)
        results = []
        if not search_text:
            return results

        for s in songs:            
            song_info_list = []
            if s["name"] is not None:
                song_info_list.append(s["name"])
            if s["album"] is not None:
                song_info_list.append(s["album"])
            if s["artist"] is not None:
                song_info_list.append(s["artist"])
            song_info = string.join(song_info_list)
            ratio = yasearch_utils.token_set_ratio(search_text.lower(), song_info.lower(), method='mean')
            res = (s, ratio)
            results.append(res)
            
        sorted_results = sorted(results, key=lambda r: r[1], reverse=True)
        return sorted_results[:limit]
    
    def search(self, search_text, offset=0, count=25, tolerance=0.75):
        limit = offset + count
        
        songs = list(self.filter(Q(name_simplified__iexact=search_text) | Q(artist_name_simplified__iexact=search_text) | Q(album_name_simplified__iexact=search_text)))
        exact_count = len(songs)
        
        if exact_count < limit:
            exclude_ids = []
            for s in songs:
                exclude_ids.append(s.id)
                
            fuzzy_limit = limit - exact_count
            res = self.search_fuzzy(search_text, fuzzy_limit, exclude_song_ids=exclude_ids)
            best_score = None
            for i in res:
                song_id = i[0]["db_id"]
                score = i[1]
                if not best_score:
                    best_score = score
                if score < best_score * tolerance:
                    break
                songs.append(YasoundSong.objects.get(id=song_id))
                
        final_songs = songs[offset:offset+count]
        return final_songs
            
            
            
            
    
class YasoundSong(models.Model):
    objects = YasoundSongManager()
    artist = models.ForeignKey(YasoundArtist, null=True, blank=True)
    album = models.ForeignKey(YasoundAlbum, null=True, blank=True)
    echonest_id = models.CharField(max_length=20, blank=True, null=True)
    lastfm_id = models.CharField(max_length=20, blank=True, null=True)
    lastfm_fingerprint_id = models.CharField(max_length=20, blank=True, null=True)
    musicbrainz_id = models.CharField(max_length=36, blank=True, null=True)
    filename = models.CharField(max_length=45)
    filesize = models.IntegerField()
    name = models.CharField(max_length=255)
    name_simplified = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255, null=True, blank=True)
    artist_name_simplified = models.CharField(max_length=255, null=True, blank=True)
    album_name = models.CharField(max_length=255, null=True, blank=True)
    album_name_simplified = models.CharField(max_length=255, null=True, blank=True)
    duration = models.IntegerField()
    danceability = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    loudness = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    energy = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tempo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tonality_mode = models.SmallIntegerField(null=True, blank=True)
    tonality_key = models.SmallIntegerField(null=True, blank=True)
    fingerprint = models.TextField(null=True, blank=True)
    fingerprint_hash = models.CharField(max_length=45, null=True, blank=True)
    echoprint_version = models.CharField(max_length=8, null=True, blank=True)
    publish_at = models.DateTimeField(blank=True, null=True)
    published = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    allowed_countries = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    cover_filename = models.CharField(max_length=45, blank=True, null=True)
    quality = models.SmallIntegerField(blank=True, null=True)
    owner_id = models.IntegerField(blank=True, null=True)
    
    
    def generate_buy_link(self):
        return buylink.generate_buy_link(self.name, self.album_name, self.artist_name)
    
    @property
    def cover_url(self):
        if not self.cover_filename:
            return None
        short_url = '%s%s' % (settings.SONG_COVER_SHORT_URL,
                         yaref_utils.convert_filename_to_filepath(self.cover_filename))
        try:
            return get_thumbnail(short_url, '256x256', crop='center').url
        except:
            return None
        

    def build_fuzzy_index(self, upsert=False, insert=True):
        return yasearch_indexer.add_song(self, upsert, insert)

    def get_song_path(self):
        return os.path.join(settings.SONGS_ROOT, yaref_utils.convert_filename_to_filepath(self.filename))
    
    def get_song_preview_path(self):
        song_path = os.path.join(settings.SONGS_ROOT, yaref_utils.convert_filename_to_filepath(self.filename))
        name, extension = os.path.splitext(song_path)
        preview = u'%s_preview64%s' % (name, extension)
        return preview


    def find_mbid(self):
        name, artist, mbid = self.name, self.artist_name, self.musicbrainz_id
        if mbid is None or len(mbid) == 0:
            metadata, valid = lastfm.find_by_name_artist(name=name, artist=artist)
            if valid and metadata.get('id') == self.lastfm_id:
                mbid = metadata.get('mbid')
                return mbid
        return None

    def find_synonyms(self):
        synonyms = []
        name, artist, album, mbid = self.name, self.artist_name, self.album_name, self.musicbrainz_id
        
        valid = False
        metadata = []
        if mbid is not None and mbid > 0:
            metadata, valid = lastfm.find_by_mbid(mbid=mbid)
        else:
            metadata, valid = lastfm.find_by_name_artist(name=name, artist=artist)
        
        if valid and self.lastfm_id and metadata.get('id') == self.lastfm_id:
            s = {
                'name': metadata.get('name'),
                'artist': metadata.get('artist'),
                'album': metadata.get('album'),
            }
            if s['name'] != name or s['artist'] != artist or s['album'] != album:
                synonyms.append(s)
            
        return synonyms
            
            
        

    class Meta:
        db_table = u'yasound_song'
        db_name = u'yasound'
        
    def __unicode__(self):
        return self.name

class YasoundSongGenre(models.Model):
    song = models.ForeignKey(YasoundSong)
    genre = models.ForeignKey(YasoundGenre)
    
    class Meta:
        db_table = u'yasound_song_genre'
        db_name = u'yasound'
        unique_together = ('song', 'genre')
        
    def __unicode__(self):
        return self.genre.name


