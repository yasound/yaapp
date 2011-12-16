from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime
from django.utils.translation import ugettext_lazy as _
import settings as yabase_settings



class SongMetadata(models.Model):    
    name = models.CharField(max_length=40)
    artist_name = models.CharField(max_length=40)
    album_name = models.CharField(max_length=40)
    track_index = models.IntegerField(null=True, blank=True)
    track_count = models.IntegerField(null=True, blank=True)
    disc_index = models.IntegerField(null=True, blank=True)
    disc_count = models.IntegerField(null=True, blank=True)
    bpm = models.FloatField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    genre = models.CharField(max_length=40, null=True, blank=True)
    picture = models.ImageField(upload_to='pictures', null=True, blank=True)
    
    def __unicode__(self):
        return self.name





class SongInstance(models.Model):
    playlist = models.ForeignKey('Playlist')
    song = models.IntegerField(null=True, blank=True) # song ID in the Song db
    play_count = models.IntegerField(default=0)
    last_play_time = models.DateTimeField(null=True, blank=True)
    yasound_score = models.FloatField(default=0)
    metadata = models.OneToOneField(SongMetadata)
    users = models.ManyToManyField(User, through='SongUser', blank=True, null=True)
    order = models.IntegerField(null=True, blank=True) # song index in the playlist
    
    def __unicode__(self):
        return str(self.song)


class SongUser(models.Model):
    song = models.ForeignKey(SongInstance, verbose_name=_('song'))
    user = models.ForeignKey(User, verbose_name=_('user'))
    
    mood = models.CharField(max_length=1, choices=yabase_settings.MOOD_CHOICES, default=yabase_settings.MOOD_NEUTRAL)

    def __unicode__(self):
        return u'%s - %s' % (self.song, self.user);
    
    class Meta:
        verbose_name = _('Song user')
        unique_together = (('song', 'user'))






class Playlist(models.Model):
    name = models.CharField(max_length=40)
    source = models.CharField(max_length=80)
    enabled = models.BooleanField(default=True)
    sync_date = models.DateTimeField(default=datetime.datetime.now)
    CRC = models.IntegerField(null=True, blank=True) # ??
    
    def __unicode__(self):
        return self.name













class Radio(models.Model):
    creator = models.ForeignKey(User, verbose_name=_('creator'), related_name='owned_radios', null=True, blank=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)    

    playlists = models.ManyToManyField(Playlist, related_name='playlists')
    
    name = models.CharField(max_length=40)
    picture = models.ImageField(upload_to='pictures', null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    genre = models.CharField(max_length=40, blank=True)
    theme = models.CharField(max_length=60, blank=True)
    
    audience_peak = models.FloatField(default=0, null=True, blank=True)
    overall_listening_time = models.FloatField(default=0, null=True, blank=True)
    
    users = models.ManyToManyField(User, through='RadioUser', blank=True, null=True)
    
    next_songs = models.ManyToManyField(SongInstance, through='NextSong')
    
    def __unicode__(self):
        return self.name;




class RadioUserManager(models.Manager):
    def get_likers(self):
        likers = self.filter(mood = yabase_settings.MOOD_LIKE)
        return likers
    
    def get_dislikers(self):
        dislikers = self.filter(mood = yabase_settings.MOOD_DISLIKE)
        return dislikers
    
    def get_favorite(self):
        favorites = self.filter(favorite=True)
        return favorites
    
    def get_connected(self):
        connected = self.filter(connected=True)
        return connected
    
    def get_selected(self):
        selected = self.filter(radio_selected=True)
        return selected


class RadioUser(models.Model):
    radio = models.ForeignKey(Radio, verbose_name=_('radio'))
    user = models.ForeignKey(User, verbose_name=_('user'))
    
    
    mood = models.CharField(max_length=1, choices=yabase_settings.MOOD_CHOICES, default=yabase_settings.MOOD_NEUTRAL)
    favorite = models.BooleanField(default=False)
    connected = models.BooleanField(default=False)
    radio_selected = models.BooleanField(default=False)
    
    # custom manager
    objects = RadioUserManager()
    
    def __unicode__(self):
        return u'%s - %s' % (self.radio, self.user);
    
    class Meta:
        verbose_name = _('Radio user')
        unique_together = (('radio', 'user'))



class WallEventManager(models.Manager):
    def get_events(self, type_value):
        events = self.filter(type=type_value)
        return events
    
    def get_join_events(self):
        events = self.get_events(yabase_settings.EVENT_JOINED)
        return events

    def get_left_events(self):
        events = self.get_events(yabase_settings.EVENT_LEFT)
        return events

    def get_message_events(self):
        events = self.get_events(yabase_settings.EVENT_MESSAGE)
        return events

    def get_song_events(self):
        events = self.get_events(yabase_settings.EVENT_SONG)
        return events


    
class WallEvent(models.Model):
    radio = models.ForeignKey(Radio)
    type = models.CharField(max_length=1, choices = yabase_settings.EVENT_TYPE_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # attributes specific to 'song' event
    song = models.ForeignKey(SongInstance, null=True, blank=True)
    old_id = models.IntegerField(null=True, blank=True)
    
    # attribute specific to 'joined', 'left' and 'message' events
    user = models.ForeignKey(User, null=True, blank=True)
    
    # attributes specific to 'message' event
    text = models.TextField(null=True, blank=True)
    animated_emoticon = models.IntegerField(null=True, blank=True)
    picture = models.ImageField(upload_to='pictures', null=True, blank=True)
    
    # custom manager
    objects = WallEventManager()
    
    def __unicode__(self):
        s = ''
        if self.type == yabase_settings.EVENT_JOINED:
            s += 'joined: '
            s += unicode(self.user)
        elif self.type == yabase_settings.EVENT_LEFT:
            s += 'left: '
            s += unicode(self.user)
        elif self.type == yabase_settings.EVENT_MESSAGE:
            s += 'message: from '
            s += unicode(self.user)
        elif self.	type == yabase_settings.EVENT_SONG:
            s += 'song: '
            s += unicode(self.song)
        return s
    
    @property
    def is_valid(self):
        valid = False
        if type == yabase_settings.EVENT_JOINED:
            valid = not (self.user is None)
        elif type == yabase_settings.EVENT_LEFT:
            valid = not (self.user is None)
        elif type == yabase_settings.EVENT_MESSAGE:
            valid = (not (self.text is None)) or (not (self.animated_emoticon is None)) or (not (self.picture is None))
        elif type == yabase_settings.EVENT_SONG:
            valid = (not (self.song is None)) and (not (self.old_id is None))
        return valid




class NextSong(models.Model):
    radio = models.ForeignKey(Radio)
    song = models.ForeignKey(SongInstance)

    order = models.IntegerField()















