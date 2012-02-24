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
from yaref.models import YasoundSong
from stats.models import RadioListeningStat
from django.db.models import Q

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
    
    yasound_song_id = models.IntegerField(_('yasound song id'), null=True, blank=True) # song ID in the Song db
    
    def __unicode__(self):
        return self.name

    class Meta:
        db_name = u'default'




class SongInstance(models.Model):
    playlist = models.ForeignKey('Playlist')
    song = models.IntegerField(null=True, blank=True) # song ID in the Song db -- this should disappear soon
    play_count = models.IntegerField(default=0)
    last_play_time = models.DateTimeField(null=True, blank=True)
    yasound_score = models.FloatField(default=0)
    metadata = models.ForeignKey(SongMetadata)
    users = models.ManyToManyField(User, through='SongUser', blank=True, null=True)
    order = models.IntegerField(null=True, blank=True) # song index in the playlist
    need_sync = models.BooleanField(default=False)
    frequency = models.FloatField(default=0.5)
    enabled = models.BooleanField(default=True)
    
    def __unicode__(self):
        return unicode(self.metadata)

    class Meta:
        db_name = u'default'
        
    def fill_bundle(self, bundle):
        likes = self.songuser_set.filter(mood=yabase_settings.MOOD_LIKE).count()
        bundle.data['likes'] = likes
        dislikes = self.songuser_set.filter(mood=yabase_settings.MOOD_DISLIKE).count()
        bundle.data['dislikes'] = dislikes
        
        if self.metadata:
            bundle.data['name'] = self.metadata.name
            bundle.data['artist'] = self.metadata.artist_name
            bundle.data['album'] = self.metadata.album_name
            bundle.data['song'] = self.metadata.yasound_song_id
        
    @property
    def song_description(self):
        try:
            song = YasoundSong.objects.get(id=self.metadata.yasound_song_id)
        except YasoundSong.DoesNotExist:
            return None
        
        desc_dict = {};
        desc_dict['id'] = self.id
        desc_dict['name'] = song.name
        desc_dict['artist'] = song.artist_name
        desc_dict['album'] = song.album_name
        if song.album:
            cover = song.album.cover_url
        elif song.cover_filename:
            cover = song.cover_url
        else:
            cover = None
        desc_dict['cover'] = cover
        
        return desc_dict
    
    @property
    def song_status(self):
        likes = SongUser.objects.likers(self).count()
        dislikes = SongUser.objects.dislikers(self).count()
        status_dict = {};
        status_dict['id'] = self.id
        status_dict['likes'] = likes
        status_dict['dislikes'] = dislikes
        return status_dict
        
class SongUserManager(models.Manager):
    def likers(self, song):
        return self.filter(song=song, mood=yabase_settings.MOOD_LIKE)
    
    def dislikers(self, song):
        return self.filter(song=song, mood=yabase_settings.MOOD_DISLIKE)

class SongUser(models.Model):
    objects = SongUserManager()
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
    radio = models.ForeignKey('Radio', related_name='playlists', blank=True, null=True)
    
    @property
    def song_count(self):
        return SongInstance.objects.filter(playlist=self).count()
    
    @property
    def matched_song_count(self):
        return SongInstance.objects.filter(playlist=self, song__isnull=False).count()
    
    @property
    def unmatched_song_count(self):
        return SongInstance.objects.filter(playlist=self, song__isnull=True).count()
    
    def __unicode__(self):
        return u'%s - %s' % (self.name, self.radio)

    class Meta:
        db_name = u'default'










RADIO_NEXT_SONGS_COUNT = 20

class RadioManager(models.Manager):
    def unlock_all(self):
        self.all().update(computing_next_songs=False)
        
    def ready_objects(self):
        return self.filter(ready=True)

class Radio(models.Model):
    objects = RadioManager()
    creator = models.ForeignKey(User, verbose_name=_('creator'), related_name='owned_radios', null=True, blank=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)    

    ready = models.BooleanField(default=False)
    
    name = models.CharField(max_length=255)
    picture = models.ImageField(upload_to=yaapp_settings.PICTURE_FOLDER, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    uuid = models.CharField(max_length=48, blank=True)
    description = models.TextField(blank=True)
    genre = models.CharField(max_length=255, blank=True, default='style_all')
    theme = models.CharField(max_length=255, blank=True)
    tags = TaggableManager(blank=True)
    
    anonymous_audience = models.IntegerField(default=0)
    audience_peak = models.FloatField(default=0, null=True, blank=True)
    current_audience_peak = models.FloatField(default=0, null=True, blank=True) # audience peak since last RadioListeningStat
    overall_listening_time = models.FloatField(default=0, null=True, blank=True)
    current_connections = models.IntegerField(default=0) # number of connections since last RadioListeningStat
    
    favorites = models.IntegerField(default=0)
    leaderboard_rank = models.IntegerField(null=True, blank=True)
    
    users = models.ManyToManyField(User, through='RadioUser', blank=True, null=True)
    
    next_songs = models.ManyToManyField(SongInstance, through='NextSong')
    computing_next_songs = models.BooleanField(default=False)
    
    current_song = models.ForeignKey(SongInstance, null=True, blank=True, verbose_name=_('current song'), related_name='current_song_radio')
    current_song_play_date = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return self.name;
    
    def save(self, *args, **kwargs):
        if not self.pk:
            # creation
            self.leaderboard_rank = Radio.objects.count()
        super(Radio, self).save(*args, **kwargs)
    
    @property
    def is_valid(self):
        valid = self.playlists.all().count() > 0
        return valid
    
    def find_new_song(self):
        songs_queryset = SongInstance.objects.filter(playlist__in=self.playlists.all(), metadata__yasound_song_id__gt=0)
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
            if total_seconds > seconds_before_replay:
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
        self.current_song_play_date = datetime.datetime.now()
        self.save()
        
        song.last_play_time = datetime.datetime.now()
        song.save()
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
        bundle.data['nb_current_users'] = self.nb_current_users
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
        self.name = n
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
    
#    @property
#    def audience(self):
#        listeners = RadioUser.objects.filter(radio=self, listening=True)
#        audience = len(listeners) + self.anonymous_audience
#        return audience
    
    def user_started_listening(self, user):
        if not user.is_anonymous():
            radio_user, created = RadioUser.objects.get_or_create(radio=self, user=user)
            radio_user.listening = True
            radio_user.save()
        else:
            self.anonymous_audience += 1
            self.save()
        
        audience = self.audience_total
        if audience > self.audience_peak:
            self.audience_peak = audience
        if audience > self.current_audience_peak:
            self.current_audience_peak = audience
        
        self.current_connections += 1    
        self.save()
            
    def user_stopped_listening(self, user, listening_duration):
        if not user.is_anonymous():
            radio_user, created = RadioUser.objects.get_or_create(radio=self, user=user)
            radio_user.listening = False
            radio_user.save()
        else:
            self.anonymous_audience -= 1
            if self.anonymous_audience < 0:
                self.anonymous_audience = 0
            self.save()
            
        self.overall_listening_time += listening_duration
        self.save() 
        

    def create_listening_stat(self):
        favorites = RadioUser.objects.get_favorite().filter(radio=self).count()
        likes = RadioUser.objects.get_likers().filter(radio=self).count()
        dislikes = RadioUser.objects.get_dislikers().filter(radio=self).count()
        stat = RadioListeningStat.objects.create(radio=self, overall_listening_time=self.overall_listening_time, audience_peak=self.current_audience_peak, connections=self.current_connections, favorites=favorites, likes=likes, dislikes=dislikes)
        
        # reset current audience peak
        audience = self.audience_total
        self.current_audience_peak = audience
        # reset current number of connections
        self.current_connections = 0
        self.save()
        return stat
    
    def relative_leaderboard(self):
        higher_radios = Radio.objects.filter(leaderboard_rank__lt=self.leaderboard_rank).order_by('leaderboard_rank').all()
        lower_radios = Radio.objects.filter(leaderboard_rank__gte=self.leaderboard_rank).exclude(id=self.id).order_by('leaderboard_rank').all()
        nb_available_higher_radios = len(higher_radios)
        nb_available_lower_radios = len(lower_radios)
        
        results = []
        nb_higher_radios = min(3, nb_available_higher_radios)
        nb_lower_radios = min(3, nb_available_lower_radios)
        for i in range(nb_available_higher_radios- nb_higher_radios, nb_available_higher_radios):
            results.append(higher_radios[i])
        results.append(self)
        for i in range(nb_lower_radios):
            results.append(lower_radios[i])
        return results
    
    def current_users(self):
        users = User.objects.filter(Q(radiouser__connected=True) | Q(radiouser__listening=True), radiouser__radio=self).all()
        return users
    
    @property
    def nb_current_users(self):
        nb_users = User.objects.filter(Q(radiouser__connected=True) | Q(radiouser__listening=True), radiouser__radio=self).count()
        return nb_users

    @property
    def audience_total(self):
        audience = self.nb_current_users
        audience += self.anonymous_audience
        return audience
    
    @property
    def unmatched_songs(self):
        songs = SongInstance.objects.filter(song=None, playlist__in=self.playlists.all())
        return songs

    @property
    def picture_url(self):
        return None
        
    class Meta:
        db_name = u'default'
        
        
def update_leaderboard():
    radios = Radio.objects.order_by('-favorites')    
    current_rank = 1
    count = 0
    last_favorites = None
    for r in radios:
        if last_favorites and r.favorites != last_favorites:
            current_rank = count + 1
        r.leaderboard_rank = current_rank
        r.save()
        count += 1
        last_favorites = r.favorites
        



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
        
    def save(self, *args, **kwargs):
        same_favorite = False
        just_connected = False
        just_started_listening = False
        if self.pk is not None:
            orig = RadioUser.objects.get(pk=self.pk)
            if orig.favorite == self.favorite:
                same_favorite = True
            if self.connected == True and orig.connected == False:
                just_connected = True
            if self.listening == True and orig.listening == False:
                just_started_listening = True 
        super(RadioUser, self).save(*args, **kwargs)
        if not same_favorite:
            radio = self.radio
            if self.favorite:
                radio.favorites += 1
            else:
                radio.favorites -= 1
                if radio.favorites < 0:
                    radio.favorites = 0
            radio.save()
            
        if just_connected:
            radio_users = RadioUser.objects.filter(user=self.user, connected=True).exclude(id=self.id)
            radio_users.update(connected=False)
        if just_started_listening:
            radio_users = RadioUser.objects.filter(user=self.user, listening=True).exclude(id=self.id)
            radio_users.update(listening=False)



class WallEventManager(models.Manager):
    def get_events(self, radio, type_value):
        events = self.filter(radio=radio, type=type_value)
        return events

    def get_message_events(self, radio):
        events = self.get_events(radio, yabase_settings.EVENT_MESSAGE)
        return events

    def get_song_events(self, radio):
        events = self.get_events(radio, yabase_settings.EVENT_SONG)
        return events
    
    def add_current_song_event(self, radio):
        song_events = self.get_song_events(radio).order_by('-start_date').all()
        if radio.current_song and (len(song_events) == 0 or radio.current_song != song_events[0].song):
            s = radio.current_song
            song_event = WallEvent.objects.create(radio=radio, type=yabase_settings.EVENT_SONG, song=s)
            song_event.start_date = radio.current_song_play_date
            song_event.save()
            
    def create_like_event(self, radio, song, user):
        self.create(radio=radio, type=yabase_settings.EVENT_LIKE, song=song, user=user)
        
    def add_like_event(self, radio, song, user):
        self.add_current_song_event(radio)
        self.create_like_event(radio, song, user)
        
  
    class Meta:
        db_name = u'default'

    
class WallEvent(models.Model):
    radio = models.ForeignKey(Radio)
    type = models.CharField(max_length=1, choices=yabase_settings.EVENT_TYPE_CHOICES)
    start_date = models.DateTimeField(auto_now_add=True)
    
    # attributes specific to 'song' event
    song = models.ForeignKey(SongInstance, null=True, blank=True)
    song_name = models.CharField(max_length=255, blank=True, null=True, default='unknown')
    song_album = models.CharField(max_length=255, blank=True, null=True, default='unknown')
    song_artist = models.CharField(max_length=255, blank=True, null=True, default='unknown')
    song_cover_filename = models.CharField(max_length=45, blank=True, null=True)
    
    # attributes specific to 'message' event
    user = models.ForeignKey(User, null=True, blank=True)
    user_name = models.CharField(max_length = 60, blank=True, null=True, default='unknown')
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
            if self.user:
                self .user_name = self.user.userprofile.name
                self.user_picture = self.user.userprofile.picture
            if self.song:
                yasound_song_id = self.song.metadata.yasound_song_id
                try:
                    yasound_song = YasoundSong.objects.get(id=yasound_song_id)
                    self.song_name = yasound_song.name
                    self.song_artist = yasound_song.artist_name
                    self.song_album = yasound_song.album_name
                    if yasound_song.album:
                        cover = yasound_song.album.cover_filename
                    elif yasound_song.cover_filename:
                        cover = yasound_song.cover_filename
                    else:
                        cover = None
                    self.song_cover_filename = cover
                except YasoundSong.DoesNotExist:
                    pass
            self.save()

    class Meta:
        db_name = u'default'



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
    
signals.post_delete.connect(next_song_deleted, sender=NextSong)

class FeaturedContent(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)    
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    activated = models.BooleanField(_('activated'), default=False)
    radios = models.ManyToManyField(Radio, through='FeaturedRadio', blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.activated:
            FeaturedContent.objects.exclude(id=self.id).update(activated=False)
        super(FeaturedContent, self).save(*args, **kwargs)
            
    class Meta:
        db_name = u'default'
        verbose_name = _('featured content')    
        
class FeaturedRadio(models.Model):
    featured_content = models.ForeignKey(FeaturedContent, verbose_name=_('featured content'))
    radio = models.ForeignKey(Radio, verbose_name=_('radio'))
    order = models.IntegerField(_('order'), default=0)

    def __unicode__(self):
        return u'%s - %s' % (self.featured_content, self.radio);
    
    class Meta:
        verbose_name = _('featured radio')
        unique_together = ('featured_content', 'radio')
        ordering = ['order',]
        db_name = u'default'
        
