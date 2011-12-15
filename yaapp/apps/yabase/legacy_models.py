# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class YasoundArtist(models.Model):
    id = models.IntegerField(primary_key=True)
    echonest_id = models.CharField(unique=True, max_length=20)
    lastfm_id = models.CharField(max_length=20)
    musicbrainz_id = models.CharField(max_length=36)
    name = models.CharField(max_length=255)
    name_simplified = models.CharField(max_length=255)
    comment = models.TextField()
    class Meta:
        db_table = u'yasound_artist'

class YasoundAlbum(models.Model):
    id = models.IntegerField(primary_key=True)
    lastfm_id = models.CharField(unique=True, max_length=20)
    musicbrainz_id = models.CharField(max_length=36)
    name = models.CharField(max_length=255)
    name_simplified = models.CharField(max_length=255)
    cover_filename = models.CharField(max_length=45)
    class Meta:
        db_table = u'yasound_album'

class YasoundGenre(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=45)
    namecanonical = models.CharField(unique=True, max_length=45)
    class Meta:
        db_table = u'yasound_genre'

class YasoundSong(models.Model):
    id = models.IntegerField(primary_key=True)
    artist = models.ForeignKey(YasoundArtist)
    album = models.ForeignKey(YasoundAlbum)
    echonest_id = models.CharField(max_length=20)
    lastfm_id = models.CharField(max_length=20)
    lastfm_fingerprint_id = models.CharField(max_length=20)
    musicbrainz_id = models.CharField(max_length=36)
    filename = models.CharField(max_length=45)
    filesize = models.IntegerField()
    name = models.CharField(max_length=255)
    name_simplified = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    artist_name_simplified = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    album_name_simplified = models.CharField(max_length=255)
    duration = models.IntegerField()
    danceability = models.DecimalField(max_digits=10, decimal_places=2)
    loudness = models.DecimalField(max_digits=10, decimal_places=2)
    energy = models.DecimalField(max_digits=10, decimal_places=2)
    tempo = models.SmallIntegerField()
    tonality_mode = models.SmallIntegerField()
    tonality_key = models.SmallIntegerField()
    fingerprint = models.TextField()
    fingerprint_hash = models.CharField(max_length=45)
    echoprint_version = models.CharField(max_length=8)
    publish_at = models.DateTimeField()
    published = models.BooleanField()
    locked = models.BooleanField()
    allowed_countries = models.CharField(max_length=255)
    comment = models.TextField()
    cover_filename = models.CharField(max_length=45)
    class Meta:
        db_table = u'yasound_song'

class YasoundSongGenre(models.Model):
    song = models.ForeignKey(YasoundSong)
    genre = models.ForeignKey(YasoundGenre)
    class Meta:
        db_table = u'yasound_song_genre'

