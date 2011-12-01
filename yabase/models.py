from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime


class Picture(models.Model):
    #file = models.FileField()
    file = models.CharField(max_length=120)
    
    def __unicode__(self):
        return self.file

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
    duration = models.FloatField() # or models.TimeField() ?
    genre = models.CharField(max_length=40, null=True, blank=True)
    picture = models.ForeignKey(Picture, null=True, blank=True)
    
    def __unicode__(self):
        return self.name

class SongInstance(models.Model):
    song = models.IntegerField(null=True, blank=True) # is it ok?
    play_count = models.IntegerField(default=0)
    last_play_time = models.DateTimeField(null=True, blank=True)
    yasound_score = models.FloatField(default=0)
    metadata = models.OneToOneField(SongMetadata)
    
    def __unicode__(self):
        return unicode(self.metadata)


class Playlist(models.Model):
    name = models.CharField(max_length=40)
    source = models.CharField(max_length=80)
    enabled = models.BooleanField(default=True)
    sync_date = models.DateTimeField(default=datetime.datetime.now)
    CRC = models.IntegerField(null=True, blank=True) # ??
    songs = models.ManyToManyField(SongInstance, related_name='songs')
    
    def __unicode__(self):
        return self.name







class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    
    join_date = models.DateTimeField(default=datetime.datetime.now)
    last_login_time = models.DateTimeField(null=True, blank=True)
    url = models.CharField(max_length=100, null=True, blank=True)
    # name ?
    twitter_account = models.CharField(max_length=60, null=True, blank=True)
    facebook_account = models.CharField(max_length=60, null=True, blank=True)
    picture = models.ForeignKey(Picture, null=True, blank=True)
    
    radios = models.ManyToManyField('Radio', related_name='radios', null=True, blank=True)
    bio_text = models.TextField(null=True, blank=True)
    favorites = models.ManyToManyField('Radio', related_name='favorites', null=True, blank=True)
    likes = models.ManyToManyField('Radio', related_name='user_likes', null=True, blank=True)
    dislikes = models.ManyToManyField('Radio', related_name='user_dislikes', null=True, blank=True)
    
    selection = models.ManyToManyField('Radio', related_name='selection', null=True, blank=True)
    last_selection_date = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
        profile, created = UserProfile.objects.get_or_create(user=instance)  

post_save.connect(create_user_profile, sender=User)

class RadioEvent(models.Model):
    TYPE_CHOICES = (
                    ('J', 'Joined'),
                    ('L', 'Left'),
                    ('M', 'Message'),
                    ('S', 'Song'),
                    )
    type = models.CharField(max_length=1, choices = TYPE_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # attributes specific to 'song' event
    song = models.ForeignKey(SongInstance, null=True, blank=True)
    old_id = models.IntegerField(null=True, blank=True)
    
    # attribute specific to 'joined', 'left' and 'message' events
    user = models.ForeignKey(UserProfile, null=True, blank=True)
    
    # attributes specific to 'message' event
    text = models.TextField(null=True, blank=True)
    animated_emoticon = models.IntegerField(null=True, blank=True)
    picture = models.ForeignKey(Picture, null=True, blank=True)
    
    def __unicode__(self):
        s = ''
        if self.type == 'J':
            s += 'joined: '
            s += unicode(self.user)
        elif self.type == 'L':
            s += 'left: '
            s += unicode(self.user)
        elif self.type == 'M':
            s += 'message: from '
            s += unicode(self.user)
        elif self.	type == 'S':
            s += 'song: '
            s += unicode(self.song)
        return s
    
    def isValid(self):
        valid = Fasle
        if type == 'J':
            valid = not (user is None)
        elif type == 'L':
            valid = not (user is None)
        elif type == 'M':
            valid = (not (text is None)) or (not (animated_emoticon is None)) or (not (picture is None))
        elif type == 'S':
            valid = (not (song is None)) and (not (old_id is None))
        return valid

class Radio(models.Model):
    name = models.CharField(max_length=40)
    playlists = models.ManyToManyField(Playlist, related_name='playlists')
    picture = models.ForeignKey(Picture, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    creation_date= models.DateTimeField(default=datetime.datetime.now)
    wall = models.ManyToManyField(RadioEvent, related_name='wall_events', null=True, blank=True)
    next_songs = models.ManyToManyField(RadioEvent, related_name='next_songs', null=True, blank=True)
    url = models.CharField(max_length=100, null=True, blank=True)
    connected_users = models.ManyToManyField(UserProfile, related_name='connected_users', null=True, blank=True)
    users_with_this_radio_as_favorite = models.ManyToManyField(UserProfile, related_name='users_with_this_radio_as_favorite',null=True, blank=True)
    audience_peak = models.FloatField(default=0, null=True, blank=True)
    likes = models.ManyToManyField(UserProfile, related_name='radio_likes', null=True, blank=True)
    dislikes = models.ManyToManyField(UserProfile, related_name='radio_dislikes', null=True, blank=True)
    overall_listening_time = models.FloatField(default=0, null=True, blank=True)
    
    def __unicode__(self):
        return self.name;















