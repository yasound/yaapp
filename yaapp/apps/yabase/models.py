from datetime import timedelta
from django.conf import settings as yaapp_settings
from django.contrib.auth.models import User, Group
from django.db import models, transaction
from django.db.models import Q, signals
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail import get_thumbnail
from stats.models import RadioListeningStat
from taggit.managers import TaggableManager
from yaref.models import YasoundSong
from yareport.task import task_report_song
import datetime
import django.db.models.options as options
import logging
import random
import settings as yabase_settings
import string
import uuid
import yasearch.indexer as yasearch_indexer
import yasearch.search as yasearch_search
import yasearch.utils as yasearch_utils
import signals as yabase_signals
from django.core.cache import cache
import json
from yacore.database import atomic_inc
import os

if yaapp_settings.ENABLE_PUSH:
    from push import install_handlers
    install_handlers()

logger = logging.getLogger("yaapp.yabase")

if not 'db_name' in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('db_name',)


class SongMetadata(models.Model):    
    name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255, blank=True)
    album_name = models.CharField(max_length=255, blank=True)
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


class SongInstanceManager(models.Manager):
    def create_from_yasound_song(self, playlist, yasound_song):
        metadatas = SongMetadata.objects.filter(name=yasound_song.name,
                                               artist_name=yasound_song.artist_name,
                                               album_name=yasound_song.album_name,
                                               yasound_song_id=yasound_song.id)[:1]
        if len(metadatas) >= 1:
            metadata = metadatas[0]
        else:
            metadata = SongMetadata(name=yasound_song.name,
                                    artist_name=yasound_song.artist_name,
                                    album_name=yasound_song.album_name,
                                    yasound_song_id=yasound_song.id)
            metadata.save()
        SongInstance.objects.get_or_create(playlist=playlist, metadata=metadata)

    def get_current_song_json(self, radio_id):
        song_json = cache.get('radio_%s.current_song.json' % (str(radio_id)), None)
        if song_json is not None:
            return song_json
        else:
            try:
                radio = Radio.objects.get(id=radio_id)
            except Radio.DoesNotExist:
                return None
            
            song_instance = None
            try:
                song_instance = radio.current_song
            except SongInstance.DoesNotExist:
                logger.error('radio.current_song failed for radio %s' % (radio.id))

            if song_instance:
                song_dict = song_instance.song_description
                if song_dict:
                    live_key = 'radio_%s.live' % (str(radio_id))
                    live_data = cache.get(live_key)
                    if live_data:
                        try:
                            song_dict['name'] = live_data['name']
                            song_dict['artist'] = live_data['artist']
                            song_dict['album'] = live_data['album']
                        except:
                            pass
                    
                    song_json = json.dumps(song_dict)
                    cache.set('radio_%s.current_song.json' % (str(radio_id)), song_json)
                    return song_json
        return None
    
    def set_current_song_json(self, radio_id, song_instance):
        song_json = None
        if song_instance:
            song_dict = song_instance.song_description
            if song_dict:
                song_json = json.dumps(song_dict)
                cache.set('radio_%s.current_song.json' % (str(radio_id)), song_json)
        return song_json

class SongInstance(models.Model):
    objects = SongInstanceManager()
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
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    
    def __unicode__(self):
        return unicode(self.metadata)

    class Meta:
        db_name = u'default'
        
    def fill_bundle(self, bundle):        
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
        cover = None
        if song.cover_filename:
            cover = song.cover_url
        if cover is None and song.album:
            cover = song.album.cover_url
            
        if cover is None:
            cover = '/media/images/default_album.jpg'
        desc_dict['cover'] = cover
        
        return desc_dict
    
    @property
    def song_status(self):
        status_dict = {};
        status_dict['id'] = self.id
        status_dict['likes'] = self.likes
        status_dict['dislikes'] = self.dislikes
        return status_dict
    
    def update_likes(self):
        likes = SongUser.objects.likers(self).count()
        self.likes = likes
        self.save()
        
    def update_dislikes(self):
        dislikes = SongUser.objects.dislikers(self).count()
        self.dislikes = dislikes
        self.save()
        
    def liked(self, user):
        radio = self.playlist.radio
        radio_creator_profile = radio.creator.userprofile
        radio_creator_profile.song_liked_in_my_radio(user_profile=user.userprofile, radio=radio, song=self)
       
    def duplicate(self, playlist):
        new_song = self.__class__.objects.create(playlist=playlist, 
                                                 order=self.order,
                                                 need_sync=self.need_sync,
                                                 metadata=self.metadata,
                                                 enabled=self.enabled)
        return new_song
         
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
        
    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = SongUser.objects.get(pk=self.pk)
            if orig.mood != self.mood:
                song_instance = self.song
                if orig.mood == yabase_settings.MOOD_LIKE:
                    song_instance.likes -= 1 # no more liked
                    song_instance.likes = max(song_instance.likes, 0)
                elif orig.mood == yabase_settings.MOOD_DISLIKE:
                    song_instance.dislikes -= 1 # no more disliked
                    song_instance.dislikes = max(song_instance.dislikes, 0)
                if self.mood == yabase_settings.MOOD_LIKE:
                    song_instance.likes += 1
                    self.song.liked(self.user)
                elif self.mood == yabase_settings.MOOD_DISLIKE:
                    song_instance.dislikes += 1
                song_instance.save()
        super(SongUser, self).save(*args, **kwargs)




class PlaylistManager(models.Manager):
    def migrate_songs_to_default(self, dry=False):
        logger.info(u"migrating all playlists to default (dry=%s)" % (dry))
        playlists = self.exclude(name='default')
        logger.info(u"found %d playlist to migrate" % (playlists.count()))
        for playlist in playlists:
            songs = SongInstance.objects.filter(playlist=playlist, playlist__radio__isnull=False)
            logger.info(u"found %d songs in playlist %s"  % (songs.count(), playlist))
            can_delete_playlist = False
            for song in songs:
                default_playlist, _created = playlist.radio.get_or_create_default_playlist()
                if not default_playlist:
                    continue 
                if dry:
                    continue
                song.playlist = default_playlist
                song.save()
                can_delete_playlist = True
            if dry:
                continue
            if can_delete_playlist:
                playlist.delete()
        logger.info("done")

class Playlist(models.Model):
    objects = PlaylistManager()
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
    
    def duplicate(self, radio):
        new_playlist = self.__class__.objects.create(name=self.name,
                                                     source=self.source,
                                                     enabled=self.enabled,
                                                     sync_date=self.sync_date,
                                                     CRC=self.CRC,
                                                     radio=radio)
        songs = SongInstance.objects.filter(playlist=self)
        for song in songs:
            song.duplicate(new_playlist)
        return new_playlist
    
    def __unicode__(self):
        return u'%s - %s' % (self.name, self.radio)

    class Meta:
        db_name = u'default'










RADIO_NEXT_SONGS_COUNT = 1

class RadioManager(models.Manager):
    def overall_listening_time(self):
        return self.all().aggregate(Sum('overall_listening_time'))['overall_listening_time__sum']
    
    def radio_for_user(self, user):
        return self.filter(creator=user)[:1][0]
    
    def unlock_all(self):
        self.all().update(computing_next_songs=False)
        
    def ready_objects(self):
        return self.filter(ready=True, creator__isnull=False)
    
    def last_indexed(self):
        doc = yasearch_indexer.get_last_radio_doc()
        if doc and doc.count() > 0:
            return self.get(id=doc[0]['db_id'])
        return None
    
    def search_fuzzy(self, search_text, limit=5):
        radios = yasearch_search.search_radio(search_text, remove_common_words=True)
        results = []
        if not search_text:
            return results

        for r in radios:
            radio_info_list = []
            if r["name"] is not None:
                radio_info_list.append(r["name"])
            if r["genre"] is not None:
                radio_info_list.append(r["genre"])
            if r["tags"] is not None:
                radio_info_list.append(r["tags"])
            radio_info = string.join(radio_info_list)
            ratio = yasearch_utils.token_set_ratio(search_text.lower(), radio_info.lower(), method='mean')
            res = (r, ratio)
            results.append(res)
            
        sorted_results = sorted(results, key=lambda i: i[1], reverse=True)
        return sorted_results[:limit]        

    def delete_fake_radios(self):
        self.filter(name__startswith='____fake____').delete()  
        
    def generate_fake_radios(self, count):
        for _i in range(0, count):
            radio_uuid = uuid.uuid4().hex
            name = '____fake____%s' % radio_uuid
            logger.info("generating radio %s" % (name))
            radio = Radio(name=name, ready=True, uuid=radio_uuid)
            radio.save()
            playlist, _created = radio.get_or_create_default_playlist()
            metadatas = SongMetadata.objects.filter(yasound_song_id__isnull=False).order_by('?')[:10]
            for metadata in metadatas:
                song_instance = SongInstance(metadata=metadata, playlist=playlist)
                song_instance.save()
                
    def fix_favorites(self):
        for r in self.all():
            r.favorites = RadioUser.objects.filter(radio=r, favorite=True).count()
            r.save()
            
    def techtour(self):
        try:
            g = Group.objects.get(name=yabase_settings.TECH_TOUR_GROUP_NAME)
        except:
            return []
        users = g.user_set.all()
        radios = self.filter(creator__in=users)
        return radios

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
    leaderboard_favorites = models.IntegerField(default=0)
    leaderboard_rank = models.IntegerField(null=True, blank=True)
    
    users = models.ManyToManyField(User, through='RadioUser', blank=True, null=True)
    
    next_songs = models.ManyToManyField(SongInstance, through='NextSong')
    computing_next_songs = models.BooleanField(default=False)
    
    current_song = models.ForeignKey(SongInstance, 
                                     null=True, 
                                     blank=True, 
                                     verbose_name=_('current song'), 
                                     related_name='current_song_radio', 
                                     on_delete=models.SET_NULL)
    
    current_song_play_date = models.DateTimeField(null=True, blank=True)
    
    def __unicode__(self):
        if self.name:
            return self.name
        elif self.creator:
            try:
                profile = self.creator.get_profile()
                return unicode(profile)
            except:
                return unicode(self.creator)
        return self.name
    
    def save(self, *args, **kwargs):
        update_mongo = False
        ready_changed = False
        if not self.pk:
            # creation
            self.leaderboard_rank = Radio.objects.count()
            update_mongo = True
        else:
            saved = Radio.objects.get(pk=self.pk)
            name_changed = self.name != saved.name
            genre_changed = self.genre != saved.genre
            tags_changed = self.tags != saved.tags
            update_mongo = name_changed or genre_changed or tags_changed
            ready_changed = self.ready != saved.ready
            
        if not self.uuid:
            self.uuid = uuid.uuid4().hex

        super(Radio, self).save(*args, **kwargs)
        if update_mongo:
            self.build_fuzzy_index(upsert=True)
        if ready_changed:
            self.now_ready()
    
    @property
    def is_valid(self):
        valid = self.playlists.all().count() > 0
        return valid
    
    @property
    def default_playlist(self):
        """
        return first enabled playlist
        """
        try:
            return self.playlists.filter(enabled=True, name='default')[:1][0]
        except:
            return None
    
    def get_or_create_default_playlist(self):
        """
        return playlist, created
        """
        playlist = self.default_playlist
        if playlist:
            return playlist, False
        playlist = Playlist(radio=self, enabled=True, name='default')
        playlist.save()
        return playlist, True
    
    def find_new_song(self):
        next_songs = NextSong.objects.filter(radio=self).values_list('song', flat=True)
        time_limit = datetime.datetime.now() - timedelta(hours=3)
        songs_queryset = SongInstance.objects.filter(playlist__in=self.playlists.all(), metadata__yasound_song_id__gt=0, enabled=True).exclude(last_play_time__gt=time_limit).exclude(id__in=next_songs).order_by('last_play_time')
        if self.current_song:
            songs_queryset = songs_queryset.exclude(id=self.current_song.id)
        
        count = songs_queryset.count() 
        
        if count == 0:
            songs_queryset = SongInstance.objects.filter(playlist__in=self.playlists.all(), metadata__yasound_song_id__gt=0, enabled=True).exclude(id__in=next_songs).order_by('last_play_time') # try without time limit
            if self.current_song:
                songs_queryset = songs_queryset.exclude(id=self.current_song.id)
            count = songs_queryset.count() 
          
        if count == 0: 
            songs_queryset = SongInstance.objects.filter(playlist__in=self.playlists.all(), metadata__yasound_song_id__gt=0, enabled=True).order_by('last_play_time') # try including current song and next songs
            count = songs_queryset.count() 
          
        if count == 0:
            print 'no available songs'
            return None 

        frequencies = songs_queryset.values_list('frequency', flat=True) 
        # use frequency * frequency to have high frequencies very different from low frequencies
        # multiply frequency weight by a date factor to have higher probabilities for songs not played since a long time (date factor = 1 for older song, 1 for more recent one)
        first_idx_factor = 1
        last_idx_factor = 0.15
        if (count-1) != 0:
            date_factor_func = lambda x: ((last_idx_factor - first_idx_factor) / (count - 1)) * x + first_idx_factor
        else:
            date_factor_func = lambda x: 1
        weights = [x*x * date_factor_func(idx) for idx, x in enumerate(frequencies)]
        r = random.random()
        sum_weight = sum(weights)
        rnd = r * sum_weight    
        index = -1
        for i, w in enumerate(weights):
            rnd -= w
            if rnd <= 0:
                index = i
                break
        if index == -1:
            if count > 0:
                index = 0
            else:
                return None
            
        song = songs_queryset.all()[index]
        return song
    
    def test_find_new_song(self, nb_tests=20):
        print 'test find_new_song for radio %s (%d)' % (self.name, self.id)
        songs = {}
        for i in range(nb_tests):
            s = self.find_new_song()
            count = songs.get(s, 0)
            count += 1
            songs[s] = count
            if i % 10 == 0:
                print '%d/%d %.2f%%' % (i, nb_tests, float(i) / float(nb_tests) * 100)
        print '%d/%d %.2f%%' % (nb_tests, nb_tests, 100)
            
        total_songs = SongInstance.objects.filter(playlist__radio=self).count()
        ready_songs = SongInstance.objects.filter(playlist__radio=self, metadata__yasound_song_id__gt=0, enabled=True).count()
        print '%d songs in the radio' % total_songs
        print '%d ready songs in the radio' % ready_songs
        
        songs_list = [(k, v) for k, v in songs.iteritems()]
        songs_list.sort(key=lambda tup: tup[1], reverse=True)
        i = 0
        for tup in songs_list:
            s = tup[0]
            count = tup[1]
            print '%4d  (%d) [%.2f %s] %s - %s - %s' % (i, count, s.frequency, s.enabled, s.metadata.artist_name, s.metadata.album_name, s.metadata.name)
            i += 1
        
        
    
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
        if self.current_song:
            task_report_song.delay(self, self.current_song)
        
        self.fill_next_songs_queue()
          
        try:
            n = NextSong.objects.get(radio=self, order=1)
        except (NextSong.DoesNotExist, NextSong.MultipleObjectsReturned):
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
        
        # TODO: use a signal instead
        song_json = SongInstance.objects.set_current_song_json(self.id, song)
        yabase_signals.new_current_song.send(sender=self, radio=self, song_json=song_json)
        
        
        self.save()
        
        song.last_play_time = datetime.datetime.now()
        song.play_count += 1
        song.save()
        self.fill_next_songs_queue()
        
        return song # SongInstance
    
    def test_get_next_song(self, nb_tests=20):
        print 'test get_next_song'
        songs = {}
        for i in range(nb_tests):
            s = self.get_next_song()
            count = songs.get(s, 0)
            count += 1
            songs[s] = count
            if i % 5 == 0:
                print '%d/%d %.2f%%' % (i, nb_tests, float(i) / float(nb_tests) * 100)
        print '%d/%d %.2f%%' % (nb_tests, nb_tests, 100)
        
        ready_songs = SongInstance.objects.filter(playlist__radio=self, metadata__yasound_song_id__gt=0, enabled=True).count()
        print '%d ready songs in the radio' % ready_songs
        
        songs_list = [(k, v) for k, v in songs.iteritems()]
        songs_list.sort(key=lambda tup: tup[1], reverse=True)
        i = 0
        for tup in songs_list:
            s = tup[0]
            count = tup[1]
            print '%4d  (%d) [%.2f] %s - %s - %s' % (i, count, s.frequency, s.metadata.artist_name, s.metadata.album_name, s.metadata.name)
            i += 1
            
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
        bundle.data['stream_url'] = self.stream_url
    
    def as_dict(self):
        likes = self.radiouser_set.filter(mood=yabase_settings.MOOD_LIKE).count()
        data = {
            'id': self.id,
            'name': self.name,
            'likes': likes,
            'favorites': self.favorites,
            'nb_current_users' : self.nb_current_users,
            'tags' : self.tags_to_string(),
            'picture': self.picture_url,
            'ready': self.ready,
            'stream_url' : self.stream_url,
        }
        return data
    
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
            radio_user, _created = RadioUser.objects.get_or_create(radio=self, user=user)
            radio_user.listening = True
            radio_user.save()
        else:
            atomic_inc(self, 'anonymous_audience', 1)
        
        audience = self.audience_total
        if audience > self.audience_peak:
            self.audience_peak = audience
        if audience > self.current_audience_peak:
            self.current_audience_peak = audience
        self.save()
        
        atomic_inc(self, 'current_connections', 1)
            
    def user_stopped_listening(self, user, listening_duration):
        if not user.is_anonymous():
            radio_user, _created = RadioUser.objects.get_or_create(radio=self, user=user)
            radio_user.listening = False
            radio_user.save()
        else:
            atomic_inc(self, 'anonymous_audience', -1)
            if self.anonymous_audience < 0:
                self.anonymous_audience = 0
                self.save()
        
        atomic_inc(self, 'overall_listening_time', listening_duration)
        yabase_signals.user_stopped_listening.send(sender=self, radio=self, user=self, duration=listening_duration)
        
    def user_connection(self, user):
        print 'user %s entered radio %s' % (user.userprofile.name, self.name)
        creator = self.creator
        if not creator:
            return
        creator_profile = creator.userprofile
        creator_profile.user_in_my_radio(creator_profile, self)
        

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
        songs = SongInstance.objects.filter(metadata__yasound_song_id=None, playlist__in=self.playlists.all())
        return songs

    @property
    def picture_url(self):
        if self.picture:
            try:
                return get_thumbnail(self.picture, '100x100', format='PNG', crop='center').url
            except:
                return yaapp_settings.DEFAULT_IMAGE
        else:
            return yaapp_settings.DEFAULT_IMAGE
        
    def set_picture(self, data):
        filename = self.build_picture_filename()
        if self.picture and len(self.picture.name) > 0:
            self.picture.delete(save=True)
        self.picture.save(filename, data, save=True)
            
    
    def build_fuzzy_index(self, upsert=False, insert=True):
        return yasearch_indexer.add_radio(self, upsert, insert)
    
    def remove_from_fuzzy_index(self):
        return yasearch_indexer.remove_radio(self)
        
    def build_picture_filename(self):
        filename = 'radio_%d_picture.png' % self.id
        return filename
    
    def delete_song_instances(self, ids):
        self.empty_next_songs_queue()

        SongInstance.objects.filter(id__in=ids, playlist__radio=self).delete()
        
    @property
    def stream_url(self):
        url = yaapp_settings.YASOUND_STREAM_SERVER_URL+ self.uuid
        return url
    
    def added_in_favorites(self, user):
        creator_profile = self.creator.userprofile
        creator_profile.my_radio_added_in_favorites(user.userprofile, self)
        
    def now_ready(self):
        self.creator.userprofile.radio_is_ready(self)
        
    def shared(self, user):
        self.creator.userprofile.my_radio_shared(user.userprofile, self)
        
    def post_message(self, user, message):
        WallEvent(radio=self,
                  start_date=datetime.datetime.now(), 
                  type=yabase_settings.EVENT_MESSAGE, 
                  user=user, 
                  text=message).save()
        
    def duplicate(self):
        new_radio = self.__class__.objects.create(creator=self.creator,
                                                  ready=self.ready,
                                                  name=u'%s - copy' % self.name,
                                                  picture=self.picture,
                                                  url=self.url,
                                                  description=self.description,
                                                  genre=self.genre,
                                                  theme=self.theme)
        new_radio.tags.set(self.tags.all())
        
        playlists = Playlist.objects.filter(radio=self)
        for playlist in playlists:
            new_playlist = playlist.duplicate(new_radio)
            new_playlist.save()
        return new_radio
    
    def set_live(self, enabled=False, name=None, album=None, artist=None):
        key = 'radio_%s.live' % (str(self.id))
        current_song_key = 'radio_%s.current_song.json' % (str(self.id))
        cache.delete(current_song_key)
        if not enabled:
            cache.delete(key)
        else:
            data = {
                'name': name,
                'album': album,
                'artist': artist
            }
            cache.set(key, data, 100*60)
            
    class Meta:
        db_name = u'default'
        
def test_random(nb_elements=50, nb_tests=50):
    print 'test random'
    print 'random between 0 and %d (int values)' % (nb_elements-1)
    print '%d tests' % nb_tests
    counts = {}
    for i in range(nb_tests):
        r = random.random()
        element = int(r * nb_elements)
        c = counts.get(element, 0)
        c += 1
        counts[element] = c
        print '%d/%d %.2f%%' % (i, nb_tests, float(i) / float(nb_tests) * 100)
    print '%d/%d %.2f%%' % (nb_tests, nb_tests, 100)
        
    counts_list = [(k, v) for k, v in counts.iteritems()]
    counts_list.sort(key=lambda tup: tup[1], reverse=True)
    i = 0
    for tup in counts_list:
        e = tup[0]
        c = tup[1]
        print '%4d  %d (%d times)' % (i, e, c)
        i += 1
    
              
def update_leaderboard():
    radios = Radio.objects.order_by('-favorites')    
    current_rank = 0
    count = 0
    last_favorites = None
    for r in radios:
        if r.favorites != last_favorites:
            current_rank = count + 1
        r.leaderboard_rank = current_rank
        r.leaderboard_favorites = r.favorites
        r.save()
        count += 1
        last_favorites = r.favorites
        
def radio_deleted(sender, instance, created=None, **kwargs):  
    if isinstance(instance, Radio):
        radio = instance
    else:
        return
    radio.remove_from_fuzzy_index()
signals.pre_delete.connect(radio_deleted, sender=Radio)



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
        if self.pk is not None: # ie : not RadioUser creation
            orig = RadioUser.objects.get(pk=self.pk)
            if orig.favorite == self.favorite:
                same_favorite = True
            if self.connected == True and orig.connected == False:
                just_connected = True
            if self.listening == True and orig.listening == False:
                just_started_listening = True 
        else:
            if self.connected == True:
                just_connected = True
            if self.listening == True:
                just_started_listening = True 
        super(RadioUser, self).save(*args, **kwargs)
        if not same_favorite:
            radio = self.radio
            radio.favorites = RadioUser.objects.filter(radio=radio, favorite=True).count()
            radio.save()
            if self.favorite:
                radio.added_in_favorites(self.user)
            
        if just_connected:
            radio_users = RadioUser.objects.filter(user=self.user, connected=True).exclude(id=self.id)
            radio_users.update(connected=False)
            self.radio.user_connection(self.user)
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
        can_add = True

        # we cannot allow consecutive duplicate like event for a song        
        previous_likes = self.filter(type=yabase_settings.EVENT_LIKE, radio=radio, user=user).order_by('-start_date')[:1]
        if previous_likes.count() != 0:
            previous = previous_likes[0]
            if previous.song_id == song.id:
                can_add = False
        
        if can_add:
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
                self.user_name = self.user.userprofile.name
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
            if self.type == yabase_settings.EVENT_MESSAGE:
                radio_creator = self.radio.creator
                if radio_creator:
                    radio_creator_profile = radio_creator.userprofile
                    radio_creator_profile.message_posted_in_my_radio(self)
            
            yabase_signals.new_wall_event.send(sender=self, wall_event=self)
    
    @property
    def user_picture_url(self):
        if self.user_picture:
            try:
                url = get_thumbnail(self.user_picture, '100x100', crop='center').url
            except:
                url = yaapp_settings.DEFAULT_IMAGE
        else:
            url = yaapp_settings.DEFAULT_IMAGE
        return url

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

class ApnsCertificateManager(models.Manager):
    def certificate_file(self, application_id, is_sandbox):
        certifs = self.filter(application_id=application_id, sandbox=is_sandbox)
        if certifs.count() == 0:
            return None
        f = certifs[0].certificate_file
        full_path = os.path.join(yaapp_settings.PROJECT_PATH, f)
        return full_path
    
    def install_defaults(self):
        self.get_or_create(application_id=yabase_settings.IPHONE_DEFAULT_APPLICATION_IDENTIFIER, sandbox=False, certificate_file='certificates/prod.pem')
        self.get_or_create(application_id=yabase_settings.IPHONE_DEFAULT_APPLICATION_IDENTIFIER, sandbox=True, certificate_file='certificates/dev.pem')
        
    def install_tech_tour(self):
        self.get_or_create(application_id=yabase_settings.IPHONE_TECH_TOUR_APPLICATION_IDENTIFIER, sandbox=False, certificate_file='certificates/techtour/prod.pem')
        self.get_or_create(application_id=yabase_settings.IPHONE_TECH_TOUR_APPLICATION_IDENTIFIER, sandbox=True, certificate_file='certificates/techtour/dev.pem')

class ApnsCertificate(models.Model):
    application_id = models.CharField(max_length=127)
    sandbox = models.BooleanField()
    certificate_file = models.CharField(max_length=255)
    objects = ApnsCertificateManager()
    


