from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from fuzzywuzzy import fuzz
import metaphone
import settings as yaref_settings

import logging
logger = logging.getLogger("yaapp.yaref")


import django.db.models.options as options
if not 'db_name' in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('db_name',)

class YasoundDoubleMetaphone(models.Model):
    value = models.CharField(max_length=255)
    def __unicode__(self):
        return self.value
    class Meta:
        db_table = u'yasound_doublemetaphone'
        db_name = u'yasound'

def _build_metaphone(sentence, exclude_common_words=True):
    values = []
    if not sentence:
        return values
    words = sorted(sentence.lower().split())
    for word in words:
        if exclude_common_words and word in yaref_settings.FUZZY_COMMON_WORDS:
            continue
        dm = metaphone.dm(word)
        value = u'%s - %s' % (dm[0], dm[1])
        values.append(value)
    return values

class YasoundArtistManager(models.Manager):
    def find_by_name(self, name, limit=None):
        values = _build_metaphone(name)
        qs = self.all()
        for value in values:
            qs = qs.filter(dms__value=value)
        if limit:
            return qs[:limit]
        return qs

class YasoundAlbumManager(models.Manager):
    def find_by_name(self, name, limit=None):
        values = _build_metaphone(name)
        qs = self.all()
        for value in values:
            qs = qs.filter(dms__value=value)
        if limit:
            return qs[:limit]
        return qs
    
class YasoundArtist(models.Model):
    objects = YasoundArtistManager()
    id = models.IntegerField(primary_key=True)
    echonest_id = models.CharField(unique=True, max_length=20)
    lastfm_id = models.CharField(max_length=20, blank=True, null=True)
    musicbrainz_id = models.CharField(max_length=36, blank=True, null=True)
    name = models.CharField(max_length=255)
    dms = models.ManyToManyField(YasoundDoubleMetaphone, null=True, blank=True)
    
    name_simplified = models.CharField(max_length=255)
    comment = models.TextField(null=True, blank=True)
    
    def build_fuzzy_index(self):
        words = sorted(self.name.lower().split())
        self.dms.clear()
        for word in words:
            dm = metaphone.dm(word)
            value = u'%s - %s' % (dm[0], dm[1])
            dm_record, created = YasoundDoubleMetaphone.objects.get_or_create(value=value)
            self.dms.add(dm_record)
    
    class Meta:
        db_table = u'yasound_artist'
        db_name = u'yasound'
    def __unicode__(self):
        return self.name

class YasoundAlbum(models.Model):
    objects = YasoundAlbumManager()
    id = models.IntegerField(primary_key=True)
    lastfm_id = models.CharField(unique=True, max_length=20, null=True, blank=True)
    musicbrainz_id = models.CharField(max_length=36, blank=True, null=True)
    name = models.CharField(max_length=255)
    name_simplified = models.CharField(max_length=255)
    cover_filename = models.CharField(max_length=45, null=True, blank=True)
    dms = models.ManyToManyField(YasoundDoubleMetaphone, null=True, blank=True)
    
    def build_fuzzy_index(self):
        words = sorted(self.name.lower().split())
        self.dms.clear()
        for word in words:
            dm = metaphone.dm(word)
            value = u'%s - %s' % (dm[0], dm[1])
            dm_record, created = YasoundDoubleMetaphone.objects.get_or_create(value=value)
            self.dms.add(dm_record)
    
    class Meta:
        db_table = u'yasound_album'
        db_name = u'yasound'
    def __unicode__(self):
        return self.name

class YasoundGenre(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45)
    namecanonical = models.CharField(unique=True, max_length=45)
    class Meta:
        db_table = u'yasound_genre'
        db_name = u'yasound'
    def __unicode__(self):
        return self.name

class YasoundSongManager(models.Manager):
    def get_query_set(self):
        return self.model.QuerySet(self.model)
    
    def test_fuzzy(self, limit=5):
#        from yaref.models import *;YasoundSong.objects.test_fuzzy()
        import random
        from time import time
        start = time()
        count = 20
        random_ids = random.sample(xrange(1000000), count)
        artist_records = list(YasoundSong.objects.filter(id__in=random_ids).all())
        
        found = 0
        errors = 0
        for i, artist in enumerate(artist_records):
            logger.debug("song id = %d" % (artist.id))
            res = self.find_fuzzy(artist.name,  artist.album_name, artist.artist_name, limit=limit) 
            if res:
                found +=1
                if res.id != artist.id:
                    errors += 1
                    found -= 1
                
            print i
        elapsed = time() - start
        logger.debug('Complete search took ' + str(elapsed) + ' seconds')
        logger.debug('Mean : ' + str(elapsed/count) + ' seconds')
        logger.debug('Found : %d/%d (%d%%), errors = %d (%d%%)' % (found, count, 100*found/count, errors, 100*errors/count))
        
    
    def find_fuzzy(self, name, album, artist, limit=5):
        from time import time
        logger.debug('fuzzy search for %s | %s | %s, limit = %r' % (name, album, artist, limit))
        start = time()
        artists = YasoundArtist.objects.find_by_name(artist, limit=limit).values_list('id', flat=True)
        albums = YasoundAlbum.objects.find_by_name(album, limit=limit).values_list('id', flat=True)
        artists = list(artists)
        albums = list(albums)
        songs = YasoundSong.objects.filter(Q(artist__id__in=artists) |
                                             Q(album__id__in=albums))
        
#        songs = YasoundSong.objects.filter(artist__id__in=artists)
        songs = songs.find_by_name(name)
        best_song = None
        best_ratio = 0
        found_count = songs.count()
        logger.debug("found %d candidate(s)" % (found_count))
        if found_count == 1:
            best_song = songs[0]
        else:
            for song in songs:
                ratio_song, ratio_album, ratio_artist = 0, 0, 0
                
                ratio_song = fuzz.token_sort_ratio(name, song.name)
                if song.album:
                    ratio_album = fuzz.token_sort_ratio(album, song.album.name)
                if song.artist:
                    ratio_artist = fuzz.token_sort_ratio(artist, song.artist.name)
            
                ratio = ratio_song + ratio_album / 4 + ratio_artist / 4
                if ratio >= best_ratio:
                    best_ratio = ratio
                    best_song = song
                    if ratio >= 100:
                        break
        elapsed = time() - start
        if best_song:
            logger.debug('candidate is %d - %s' % (best_song.id, best_song.name.replace("\n", " ")))
        else:
            logger.debug('no candidate found')
        logger.debug('Search took %d seconds' % (elapsed))
        return best_song
    
class YasoundSong(models.Model):
    objects = YasoundSongManager()
    id = models.IntegerField(primary_key=True)
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
    publish_at = models.DateTimeField()
    published = models.BooleanField()
    locked = models.BooleanField()
    allowed_countries = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    cover_filename = models.CharField(max_length=45, blank=True, null=True)
    dms = models.ManyToManyField(YasoundDoubleMetaphone, null=True, blank=True)

    def build_fuzzy_index(self):
        words = sorted(self.name.lower().split())
        self.dms.clear()
        for word in words:
            dm = metaphone.dm(word)
            value = u'%s - %s' % (dm[0], dm[1])
            dm_record, created = YasoundDoubleMetaphone.objects.get_or_create(value=value)
            self.dms.add(dm_record)

    class QuerySet(QuerySet):
        def find_by_name(self, name, limit=None):
            values = _build_metaphone(name)
            qs = self.all()
            for value in values:
                qs = qs.filter(dms__value=value)
            if limit:
                return qs[:limit]
            return qs

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
    def __unicode__(self):
        return self.genre.name


