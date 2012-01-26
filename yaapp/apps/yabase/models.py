from django.conf import settings as yaapp_settings
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager
import datetime
import random
import settings as yabase_settings
import string

import django.db.models.options as options
if not 'db_name' in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('db_name',)

class SongMetadata(models.Model):    
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    track_index = models.IntegerField(null=True, blank=True)
    track_count = models.IntegerField(null=True, blank=True)
    disc_index = models.IntegerField(null=True, blank=True)
    disc_count = models.IntegerField(null=True, blank=True)
    bpm = models.FloatField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)
    genre = models.CharField(max_length=255, null=True, blank=True)
    picture = models.ImageField(upload_to=yaapp_settings.PICTURE_FOLDER, null=True, blank=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        db_name = u'default'




class SongInstance(models.Model):
    playlist = models.ForeignKey('Playlist')
    song = models.IntegerField(null=True, blank=True) # song ID in the Song db
    play_count = models.IntegerField(default=0)
    last_play_time = models.DateTimeField(null=True, blank=True)
    yasound_score = models.FloatField(default=0)
    metadata = models.ForeignKey(SongMetadata)
    users = models.ManyToManyField(User, through='SongUser', blank=True, null=True)
    order = models.IntegerField(null=True, blank=True) # song index in the playlist
    
    def __unicode__(self):
        return unicode(self.metadata)

    class Meta:
        db_name = u'default'
        
    def fill_bundle(self, bundle):
        likes = self.songuser_set.filter(mood=yabase_settings.MOOD_LIKE).count()
        bundle.data['likes'] = likes
        dislikes = self.songuser_set.filter(mood=yabase_settings.MOOD_DISLIKE).count()
        bundle.data['dislikes'] = dislikes
        


class SongUser(models.Model):
    song = models.ForeignKey(SongInstance, verbose_name=_('song'))
    user = models.ForeignKey(User, verbose_name=_('user'))
    
    mood = models.CharField(max_length=1, choices=yabase_settings.MOOD_CHOICES, default=yabase_settings.MOOD_NEUTRAL)

    def __unicode__(self):
        return u'%s - %s' % (self.song, self.user);
    
    class Meta:
        verbose_name = _('Song user')
        unique_together = (('song', 'user'))
        db_name = u'default'






class Playlist(models.Model):
    name = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    enabled = models.BooleanField(default=True)
    sync_date = models.DateTimeField(default=datetime.datetime.now)
    CRC = models.IntegerField(null=True, blank=True) # ??
    
    def __unicode__(self):
        return self.name

    class Meta:
        db_name = u'default'










RADIO_NEXT_SONGS_COUNT = 20

class RadioManager(models.Manager):
    def unlock_all(self):
        self.all().update(computing_next_songs=False)

class Radio(models.Model):
    objects = RadioManager()
    creator = models.ForeignKey(User, verbose_name=_('creator'), related_name='owned_radios', null=True, blank=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)    

    playlists = models.ManyToManyField(Playlist, related_name='playlists', null=True, blank=True)
    ready = models.BooleanField(default=False)
    
    name = models.CharField(max_length=255)
    picture = models.ImageField(upload_to=yaapp_settings.PICTURE_FOLDER, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    uuid = models.CharField(max_length=48, blank=True)
    description = models.TextField(blank=True)
    genre = models.CharField(max_length=255, blank=True)
    theme = models.CharField(max_length=255, blank=True)
    tags = TaggableManager(blank=True)
    
    anonymous_audience = models.IntegerField(default=0)
    audience_peak = models.FloatField(default=0, null=True, blank=True)
    overall_listening_time = models.FloatField(default=0, null=True, blank=True)
    
    users = models.ManyToManyField(User, through='RadioUser', blank=True, null=True)
    
    next_songs = models.ManyToManyField(SongInstance, through='NextSong')
    computing_next_songs = models.BooleanField(default=False)
    
    current_song = models.ForeignKey(SongInstance, null=True, blank=True, verbose_name=_('current song'), related_name='current_song_radio') 
    
    def __unicode__(self):
        return self.name;
    
    @property
    def is_valid(self):
        valid = self.playlists.count() > 0
        return valid
    
    def find_new_song(self):
        songs_queryset = SongInstance.objects.filter(playlist__in=self.playlists.all(), song__gt=0)
        songs = songs_queryset.all()
        count = len(songs)
        if count == 0:
            return None
        
        seconds_before_replay = 60 * 60 # at least 60 minutes before replaying the same song
        now = datetime.datetime.now()
        i = random.randint(0, count - 1)
        first = i
        while songs[i].last_play_time:
            delta = now - songs[i].last_play_time
            total_seconds = delta.days * 86400 + delta.seconds
            if total_seconds <= seconds_before_replay:
                break
            i += 1
            i %= count
            if i == first:
                break
        
        s = songs[i]
        return s
    
    def fill_next_songs_queue(self):
        while self.next_songs.count() < RADIO_NEXT_SONGS_COUNT:
            s = self.find_new_song()
            if s == None:
                break;
            o = len(self.next_songs.all()) + 1
            NextSong.objects.create(radio=self, song=s, order=o)
            
    def empty_next_songs_queue(self):
        signals.post_delete.disconnect(next_song_deleted, sender=NextSong)
        NextSong.objects.filter(radio=self).delete()
        signals.post_delete.connect(next_song_deleted, sender=NextSong)
    
    def get_next_song(self):
        self.fill_next_songs_queue()
            
        try:
            n = NextSong.objects.get(radio=self, order=1)
        except NextSong.DoesNotExist:
            try:
                self.empty_next_songs_queue()
                self.fill_next_songs_queue()
                n = NextSong.objects.get(radio=self, order=1)
            except NextSong.DoesNotExist:
                print 'cannot get next song for radio: %s' % unicode(self)
                return None 
        
        song = n.song
        n.delete()
        
        # update current song
        self.current_song = song
        
        song.last_play_time = datetime.datetime.now()
        self.fill_next_songs_queue()
        return song # SongInstance
            
    def tags_to_string(self):
        first = True
        tags_str = ''
        for tag in self.tags.all():
            t = tag.name
            if first:
                tags_str += t
                first = False
            else:
                tags_str += ','
                tags_str += t
        return tags_str
    
    def set_tags(self, tags_string):
        separator = ','
        tags_array = string.split(tags_string, separator)
        self.tags.clear()
        for tag in tags_array:
            self.tags.add(tag)
        
    def fill_bundle(self, bundle):
        likes = self.radiouser_set.filter(mood=yabase_settings.MOOD_LIKE).count()
        bundle.data['likes'] = likes
        favorites = self.radiouser_set.filter(favorite=True).count()
        bundle.data['favorites'] = favorites
        connected_users = self.radiouser_set.filter(connected=True).count()
        bundle.data['connected_users'] = connected_users
        listeners = self.radiouser_set.filter(listening=True).count()
        bundle.data['listeners'] = listeners
        bundle.data['tags'] = self.tags_to_string()
        
    def update_with_data(self, data):
        if 'description' in data:
            self.description = data['description']
        if 'url' in data:
            self.url = data['url']
        if 'tags' in data:
            self.set_tags(data['tags'])
        self.save()
        
    def create_name(self, user):
        n = user.userprofile.name
        if not n:
            n = user.username
        self.name = n + "'s radio"
        self.save()

    def unlock(self):
        self.computing_next_songs = False
        self.save()
    
    def lock(self):
        self.computing_next_songs = True
        self.save()
    
    @property
    def is_locked(self):
        return self.computing_next_songs

    class Meta:
        db_name = u'default'



class RadioUserManager(models.Manager):
    def get_likers(self):
        likers = self.filter(mood=yabase_settings.MOOD_LIKE)
        return likers
    
    def get_dislikers(self):
        dislikers = self.filter(mood=yabase_settings.MOOD_DISLIKE)
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

    class Meta:
        db_name = u'default'



class RadioUser(models.Model):
    radio = models.ForeignKey(Radio, verbose_name=_('radio'))
    user = models.ForeignKey(User, verbose_name=_('user'))
    
    
    mood = models.CharField(max_length=1, choices=yabase_settings.MOOD_CHOICES, default=yabase_settings.MOOD_NEUTRAL)
    favorite = models.BooleanField(default=False)
    connected = models.BooleanField(default=False)
    radio_selected = models.BooleanField(default=False)
    listening = models.BooleanField(default=False)
    
    # custom manager
    objects = RadioUserManager()
    
    def __unicode__(self):
        return u'%s - %s' % (self.radio, self.user);
    
    class Meta:
        verbose_name = _('Radio user')
        unique_together = (('radio', 'user'))
        db_name = u'default'



class WallEventManager(models.Manager):
    def get_events(self, type_value):
        events = self.filter(type=type_value)
        return events

    def get_message_events(self):
        events = self.get_events(yabase_settings.EVENT_MESSAGE)
        return events

    def get_song_events(self):
        events = self.get_events(yabase_settings.EVENT_SONG)
        return events
  
    class Meta:
        db_name = u'default'

    
class WallEvent(models.Model):
    radio = models.ForeignKey(Radio)
    type = models.CharField(max_length=1, choices=yabase_settings.EVENT_TYPE_CHOICES)
    start_date = models.DateTimeField(auto_now_add=True)
    
    # attributes specific to 'song' event
    song = models.ForeignKey(SongInstance, null=True, blank=True)
    song_name = models.CharField(max_length=255, blank=True)
    song_album = models.CharField(max_length=255, blank=True)
    song_artist = models.CharField(max_length=255, blank=True)
    song_cover_filename = models.CharField(max_length=45, blank=True)
    
    # attributes specific to 'message' event
    user = models.ForeignKey(User, null=True, blank=True)
    user_name = models.CharField(max_length = 60, blank=True)
    user_picture = models.ImageField(upload_to=yaapp_settings.PICTURE_FOLDER, null=True, blank=True)
    
    text = models.TextField(null=True, blank=True)
    animated_emoticon = models.IntegerField(null=True, blank=True)
    picture = models.ImageField(upload_to=yaapp_settings.PICTURE_FOLDER, null=True, blank=True)
    
    # custom manager
    objects = WallEventManager()
    
    def __unicode__(self):
        s = ''
        if self.type == yabase_settings.EVENT_MESSAGE:
            s = '(%s) %s: "%s"' % (self.radio.name, self.user_name, self.text)
        elif self.	type == yabase_settings.EVENT_SONG:
            s = '(%s) song: "%s - %s - %s"' % (self.radio.name, self.song_name, self.song_artist, self.song_album)
        return s
    
    @property
    def is_valid(self):
        if not self.radio:
            return False
        valid = False
        if self.type == yabase_settings.EVENT_MESSAGE:
            valid = (not (self.text is None)) or (not (self.animated_emoticon is None)) or (not (self.picture is None))
        elif self.type == yabase_settings.EVENT_SONG:
            valid = not (self.song is None)
        return valid
    
    def save(self, *args, **kwargs):
        creation = False
        if not self.pk:
            creation = True
           
        super(WallEvent, self).save(*args, **kwargs)
        
        if creation:
            if self.type == yabase_settings.EVENT_MESSAGE:
                self .user_name = self.user.userprofile.name
                self.user_picture = self.user.userprofile.picture
            elif self.type == yabase_settings.EVENT_SONG:
                self.song_name = self.song.name
                self.song_artist = self.song.artist_name
                self.song_album = self.song.album_name
                if self.song.album:
                    cover = self.song.album.cover_filename
                elif self.song.cover_filename:
                    cover = self.song.cover_filename
                else:
                    cover = None
                self.song_cover_filename = cover
            self.save()

    class Meta:
        db_name = u'default'
        
#    def save(self, *args, **kwargs):
#        super(WallEvent, self).save(*args, **kwargs)
#        
#        if self.type == yabase_settings.EVENT_JOINED:
#            radiouser, created = RadioUser.objects.get_or_create(user=self.user, radio=self.radio)
#            radiouser.connected = True
#            radiouser.save()
#            
#        elif self.type == yabase_settings.EVENT_LEFT:
#            radiouser, created = RadioUser.objects.get_or_create(user=self.user, radio=self.radio)
#            radiouser.connected = False
#            radiouser.save()
#            
#        elif self.type == yabase_settings.EVENT_STARTED_LISTEN:
#            if self.user:
#                radiouser, created = RadioUser.objects.get_or_create(user=self.user, radio=self.radio)
#                radiouser.listening = True
#                radiouser.save()
#            else:
#                self.radio.anonymous_audience += 1
#                self.radio.save()
#            
#            
#            listeners = RadioUser.objects.filter(radio=self.radio, listening=True)
#            audience = len(listeners) + self.radio.anonymous_audience
#            if audience > self.radio.audience_peak:
#                self.radio.audience_peak = audience
#                self.radio.save()
#            
#        elif self.type == yabase_settings.EVENT_STOPPED_LISTEN:
#            if self.user:
#                radiouser, created = RadioUser.objects.get_or_create(user=self.user, radio=self.radio)
#                radiouser.listening = False
#                radiouser.save()
#                            
#                last_start = WallEvent.objects.filter(user=self.user, radio=self.radio, type=yabase_settings.EVENT_STARTED_LISTEN).order_by('-start_date')[0]
#                last_stop = WallEvent.objects.filter(user=self.user, radio=self.radio, type=yabase_settings.EVENT_STOPPED_LISTEN).order_by('-start_date')[0]
#                duration = last_stop.start_date - last_start.start_date
#                seconds = duration.days * 86400 + duration.seconds
#                self.radio.overall_listening_time += seconds
#                self.radio.save()
#            
#            elif self.text:
#                self.radio.anonymous_audience -= 1
#                self.radio.save()
#                
#                last_start = WallEvent.objects.filter(text=self.text, radio=self.radio, type=yabase_settings.EVENT_STARTED_LISTEN).order_by('-start_date')[0]
#                last_stop = WallEvent.objects.filter(text=self.text, radio=self.radio, type=yabase_settings.EVENT_STOPPED_LISTEN).order_by('-start_date')[0]
#                duration = last_stop.start_date - last_start.start_date
#                seconds = duration.days * 86400 + duration.seconds
#                self.radio.overall_listening_time += seconds
#                self.radio.save()



class NextSong(models.Model):
    radio = models.ForeignKey(Radio)
    song = models.ForeignKey(SongInstance)

    order = models.IntegerField()

    class Meta:
        db_name = u'default'

    def __unicode__(self):
        s = '%s - %s - %d' % (unicode(self.radio), unicode(self.song), self.order)
        return s;
    
    @transaction.commit_on_success
    def save(self, *args, **kwargs):
        old_order = int(self.order)
        new_order = int(self.order)
        creation = False
        if self.pk:
            in_db = NextSong.objects.get(pk=self.pk)
            old_order = int(in_db.order)
        else:
            creation = True
        
        if creation:
            to_update = NextSong.objects.filter(radio=self.radio, order__gte=self.order).order_by('-order')
            for i in to_update:
                i.order += 1
                super(NextSong, i).save()
        
        super(NextSong, self).save(*args, **kwargs)
        
        if old_order != new_order:
            if new_order < old_order:
                to_update = NextSong.objects.filter(radio=self.radio, order__range=(new_order, old_order - 1)).exclude(pk=self.pk).order_by('-order')
                for i in to_update:
                    i.order += 1
                    super(NextSong, i).save()
            else:
                to_update = NextSong.objects.filter(radio=self.radio, order__range=(old_order + 1, new_order)).exclude(pk=self.pk).order_by('order')
                for i in to_update:
                    i.order -= 1
                    super(NextSong, i).save()
        


def next_song_deleted(sender, instance, created=None, **kwargs):
    """
    handle next song deletion
    """
    if isinstance(instance, NextSong):
        next_song = instance
    else:
        return
    
    order = next_song.order
    to_update = NextSong.objects.filter(radio=next_song.radio, order__gt=order).exclude(id=next_song.id)
    for n in to_update:
        n.order -= 1
        super(NextSong, n).save()
    next_song.radio.fill_next_songs_queue()
signals.post_delete.connect(next_song_deleted, sender=NextSong)


