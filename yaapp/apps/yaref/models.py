"""
Contains models related to yasound database (ie all the songs)
"""
from django.db import models
from django.conf import settings
from fuzzywuzzy import fuzz
import mongo
import logging
from time import time
import utils as yaref_utils
logger = logging.getLogger("yaapp.yaref")

import django.db.models.options as options
if not 'db_name' in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('db_name',)

def build_mongodb_index(upsert=False, erase=False):
    """
    build mongodb fuzzy index : if upsert=False then document is inserted without checking for existent one
    """
    if erase:
        logger.info("deleting index")
        mongo.erase_index()
    
    if upsert:
        logger.info("using upsert")
    else:
        logger.info("not using upsert")

    songs = YasoundSong.objects.all()
    last_indexed = YasoundSong.objects.last_indexed()
    if last_indexed:
        logger.info("last indexed = %d" % (last_indexed.id))
        songs = songs.filter(id__gt=last_indexed.id)
    count = songs.count()
    logger.info("processing %d songs" % (count))
    if count > 0:
        start = time()
        if upsert:
            for i, song in enumerate(yaref_utils.queryset_iterator(songs)):
                song.build_fuzzy_index(upsert=True)
                if i % 10000 == 0:
                    elapsed = time() - start
                    logger.info("processed %d/%d (%d%%) in %s seconds" % (i, count, 100*i/count, str(elapsed)))
                start = time()
        else:
            bulk = mongo.begin_bulk_insert()
            for i, song in enumerate(yaref_utils.queryset_iterator(songs)):
                bulk.append(song.build_fuzzy_index(upsert=False, insert=False))
                if i % 10000 == 0:
                    mongo.commit_bulk_insert(bulk)
                    bulk = mongo.begin_bulk_insert()
                    elapsed = time() - start
                    logger.info("processed %d/%d (%d%%) in % seconds" % (i, count, 100*i/count, str(elapsed)))
                    start = time()
            mongo.commit_bulk_insert(bulk)
    
    logger.info("building mongodb index")
    mongo.build_index()      
    logger.info("done")    

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
        
        return '%s%s' % (settings.ALBUM_COVER_URL,
                         yaref_utils.convert_filename_to_filepath(self.cover_filename))
    
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
        doc = mongo.get_last_doc()
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
        songs = mongo.find_song(name, album, artist, remove_common_words=True)
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
    
    def search_fuzzy(self, search_text, limit=20):
        print 'search fuzzy "%s"' % search_text
        songs = mongo.search_song(search_text, remove_common_words=True)
        print '%d songs' % songs.count()
        results = []
        if not search_text:
            return results
        
        SONG_COEFF = 4
        ARTIST_COEFF = 1
        ALBUM_COEFF = 1
        total_coeffs = SONG_COEFF + ARTIST_COEFF + ALBUM_COEFF
        for s in songs:
            ratio_song, ratio_album, ratio_artist = 0, 0, 0
            if s["name"] is not None:
                ratio_song = fuzz.token_sort_ratio(search_text, s["name"])
                
            if s["album"] is not None:
                ratio_album = fuzz.token_sort_ratio(search_text, s["album"])

            if s["artist"] is not None:
                ratio_artist = fuzz.token_sort_ratio(search_text, s["artist"])
            ratio = (SONG_COEFF * ratio_song + ALBUM_COEFF * ratio_album + ARTIST_COEFF * ratio_artist) / total_coeffs
            res = (s, ratio)
            results.append(res)
            
        sorted_results = sorted(results, key=lambda r: r[1], reverse=True)
        return sorted_results[:limit]
            
            
    
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
    artist_name = models.CharField(max_length=255)
    artist_name_simplified = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    album_name_simplified = models.CharField(max_length=255)
    duration = models.IntegerField()
    danceability = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    loudness = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    energy = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tempo = models.SmallIntegerField(null=True, blank=True)
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
    
    @property
    def cover_url(self):
        return None
        

    def build_fuzzy_index(self, upsert=False, insert=True):
        return mongo.add_song(self, upsert, insert)

    class Meta:
        db_table = u'yasound_song'
        db_name = u'yasound'
        
    def __unicode__(self):
        return self.name

class YasoundSongGenre(models.Model):
    song = models.ForeignKey(YasoundSong, primary_key=True)
    genre = models.ForeignKey(YasoundGenre)
    
    class Meta:
        db_table = u'yasound_song_genre'
        db_name = u'yasound'
        unique_together = ('song', 'genre')
        
    def __unicode__(self):
        return self.genre.name


