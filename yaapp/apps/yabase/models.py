from datetime import timedelta
from django.conf import settings as yaapp_settings
from django.contrib.auth.models import User, Group
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import models, transaction
from django.db.models import Q, signals
from django.db.models.aggregates import Sum
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from sorl.thumbnail import get_thumbnail, delete
from stats.models import RadioListeningStat
from taggit.managers import TaggableManager
from transmeta import TransMeta
from yacore.database import atomic_inc
from yacore.http import absolute_url
from yacore.tags import clean_tags, clean_tag
from yametrics.matching_errors import MatchingErrorsManager
from yaref.models import YasoundSong
from yareport.task import task_report_song
from yasearch.utils import get_simplified_name
import datetime
import django.db.models.options as options
import json
import logging
import hashlib
import os
import random
import settings as yabase_settings
import signals as yabase_signals
import string
import uuid
import yasearch.indexer as yasearch_indexer
import yasearch.search as yasearch_search
import yasearch.utils as yasearch_utils
from django.db.models import F
from django.template.defaultfilters import striptags
from yageoperm.models import Country
from django.utils.html import urlize, linebreaks
from yametadata.kfm import find_metadata as kfm_find_metadata

logger = logging.getLogger("yaapp.yabase")

if not 'db_name' in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('db_name',)

class SongMetadataManager(models.Manager):
    def build_hash_name(self):
        qs = self.filter(hash_name__isnull=True)
        for sm in qs:
            sm.calculate_hash_name(commit=True)

class SongMetadata(models.Model):
    objects = SongMetadataManager()
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
    picture = models.ImageField(upload_to=yaapp_settings.RADIO_PICTURE_FOLDER, null=True, blank=True)

    yasound_song_id = models.IntegerField(_('yasound song id'), null=True, blank=True) # song ID in the Song db

    hash_name = models.CharField(max_length=32, blank=True, null=True)

    def calculate_hash_name(self, commit=True):
        hash_name = hashlib.md5()
        hash_name.update(get_simplified_name(self.name))
        hash_name.update(get_simplified_name(self.album_name))
        hash_name.update(get_simplified_name(self.artist_name))
        hash_name = hash_name.hexdigest()
        self.hash_name = hash_name
        if commit:
            self.save()
        return hash_name


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
        return SongInstance.objects.get_or_create(playlist=playlist, metadata=metadata)

    def get_current_song_json(self, radio_id):
        song_json = cache.get('radio_%s.current_song.json' % (str(radio_id)), None)
        if song_json is not None:
            return song_json
        else:
            try:
                radio = Radio.objects.select_related('radioways_radio').get(id=radio_id)
            except Radio.DoesNotExist:
                return None

            if radio.origin == yabase_settings.RADIO_ORIGIN_RADIOWAYS:
                radioways_radio = radio.radioways_radio
                song_dict = radioways_radio.current_song
                song_json = json.dumps(song_dict)
                cache.set('radio_%s.current_song.json' % (str(radio_id)), song_json, 10)
                return song_json
            elif radio.origin == yabase_settings.RADIO_ORIGIN_KFM:
                song_dict = kfm_find_metadata()
                song_json = json.dumps(song_dict)
                cache.set('radio_%s.current_song.json' % (str(radio_id)), song_json, 10)
                return song_json

            song_instance = None
            try:
                song_instance = radio.current_song
            except SongInstance.DoesNotExist:
                logger.error('radio.current_song failed for radio %s' % (radio.id))

            if song_instance:
                # in this case, name/artist/album contain information from yasound db on the server
                song_dict = song_instance.song_description(info_from_yasound_db=True)
                if song_dict:
                    live_data = radio.live_data()
                    if live_data:
                        try:
                            song_dict['id'] = live_data['id']
                            song_dict['name'] = live_data['name']
                            song_dict['artist'] = live_data['artist']
                            song_dict['album'] = live_data['album']
                            song_dict['cover'] = live_data['cover']
                            song_dict['large_cover'] = live_data['large_cover']
                        except:
                            pass

                    song_json = json.dumps(song_dict)
                    cache.set('radio_%s.current_song.json' % (str(radio_id)), song_json)
                    return song_json
        return None

    def set_current_song_json(self, radio, song_instance):
        song_json = None
        song_dict = []
        if song_instance:
            song_dict = song_instance.song_description(info_from_yasound_db=True)
            if song_dict:
                live_data = radio.live_data()
                if live_data:
                    try:
                        song_dict['id'] = live_data['id']
                        song_dict['name'] = live_data['name']
                        song_dict['artist'] = live_data['artist']
                        song_dict['album'] = live_data['album']
                        song_dict['cover'] = live_data['cover']
                        song_dict['large_cover'] = live_data['large_cover']
                    except:
                        pass

                song_json = json.dumps(song_dict)
                cache.set('radio_%s.current_song.json' % (str(radio.id)), song_json)
        return song_json, song_dict

class SongInstance(models.Model):
    objects = SongInstanceManager()
    playlist = models.ForeignKey('Playlist')
    song = models.IntegerField(null=True, blank=True) # song ID in the Song db -- this should disappear soon
    play_count = models.IntegerField(default=0)
    last_play_time = models.DateTimeField(null=True, blank=True)
    yasound_score = models.FloatField(default=0)
    metadata = models.ForeignKey(SongMetadata)
    users = models.ManyToManyField(User, through='SongUser', blank=True, null=True)
    order = models.IntegerField(null=True, blank=True) # when it's changed, order for other songs from the playlist is updated
    need_sync = models.BooleanField(default=False)
    frequency = models.FloatField(default=0.5)
    enabled = models.BooleanField(default=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    def __unicode__(self):
        return unicode(self.metadata)

    class Meta:
        db_name = u'default'

    def song_description(self, include_cover=True, info_from_yasound_db=True):
        try:
            song = YasoundSong.objects.get(id=self.metadata.yasound_song_id)
        except YasoundSong.DoesNotExist:
            return None

        desc_dict = {};
        desc_dict['id'] = self.id

        desc_dict['name_server'] = song.name
        desc_dict['artist_server'] = song.artist_name
        desc_dict['album_server'] = song.album_name
        desc_dict['name_client'] = self.metadata.name
        desc_dict['artist_client'] = self.metadata.artist_name
        desc_dict['album_client'] = self.metadata.album_name

        desc_dict['name_simplified'] = song.name_simplified
        desc_dict['artist_simplified'] = song.artist_name_simplified
        desc_dict['album_simplified'] = song.album_name_simplified

        if info_from_yasound_db:
            desc_dict['name'] = desc_dict['name_server']
            desc_dict['artist'] = desc_dict['artist_server']
            desc_dict['album'] = desc_dict['album_server']
        else: # info from client's playlists
            desc_dict['name'] = desc_dict['name_client']
            desc_dict['artist'] = desc_dict['artist_client']
            desc_dict['album'] = desc_dict['album_client']

        desc_dict['likes'] = self.likes
        desc_dict['enabled'] = self.enabled
        desc_dict['frequency'] = self.frequency
        desc_dict['last_play_time'] = self.last_play_time.isoformat() if self.last_play_time is not None else None
        desc_dict['need_sync'] = self.need_sync
        desc_dict['order'] = self.order


        cover = None
        large_cover = None
        if include_cover:
            if song.cover_filename:
                cover = song.cover_url
                large_cover = song.large_cover_url
            if cover is None and song.album:
                cover = song.album.cover_url
                large_cover = song.album.large_cover_url

        if cover is None:
            cover = '/media/images/default_album.jpg'
            large_cover = '/media/images/default_album.jpg'
        desc_dict['cover'] = cover
        desc_dict['large_cover'] = large_cover

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
        radio_creator_profile = radio.creator.get_profile()
        radio_creator_profile.song_liked_in_my_radio(user_profile=user.get_profile(), radio=radio, song=self)

    def duplicate(self, playlist):
        new_song = self.__class__.objects.create(playlist=playlist,
                                                 order=self.order,
                                                 need_sync=self.need_sync,
                                                 metadata=self.metadata,
                                                 enabled=self.enabled)
        return new_song

    def save(self, *args, **kwargs):
        old_order = None
        new_order = self.order
        if self.pk:
            old_order = SongInstance.objects.get(pk=self.pk).order

        # be sure to have order value in the good range
        if new_order is not None:
            nb_songs_with_order = SongInstance.objects.filter(playlist=self.playlist, order__isnull=False).count()
            if old_order is None:
                max_new_order = nb_songs_with_order
            else:
                max_new_order = nb_songs_with_order - 1
            new_order = min(max_new_order, new_order)
            new_order = max(0, new_order)
            self.order = new_order
        super(SongInstance, self).save(*args, **kwargs)

        if new_order == old_order:
            return;
        p = self.playlist
        if new_order is not None and old_order is None: # insertion
            SongInstance.objects.filter(playlist=p, order__gte=new_order, order__isnull=False).exclude(id=self.id).update(order=F('order') + 1) # increment order
        elif new_order is None and old_order is not None: # order set to None
            SongInstance.objects.filter(playlist=p, order__gt=old_order, order__isnull=False).exclude(id=self.id).update(order=F('order') - 1) # decrement order
        elif new_order is not None and old_order is not None: # new_order and old_order not None
            if new_order > old_order:
                SongInstance.objects.filter(playlist=p, order__gt=old_order, order__lte=new_order, order__isnull=False).exclude(id=self.id).update(order=F('order') - 1) # decrement
            elif old_order > new_order:
                SongInstance.objects.filter(playlist=p, order__gte=new_order, order__lt=old_order, order__isnull=False).exclude(id=self.id).update(order=F('order') + 1) # increment


def song_instance_deleted(sender, instance, created=None, **kwargs):
    """
    when a song instance is deleted, we must be sure that
    the radio.current_song is set to NULL
    """
    if isinstance(instance, SongInstance):
        song_instance = instance
    else:
        return

    try:
        radio = song_instance.playlist.radio
        if radio.current_song_id == song_instance.id:
            radio.current_song = None
            radio.save()
            radio.clear_current_song_json_cache()
    except:
        logger.error('no radio or playlist for song instance %s' % (song_instance.id))

    if song_instance.order is not None:
        # decrement order for song instances with order greater than this song
        SongInstance.objects.filter(playlist=song_instance.playlist, order__gt=song_instance.order).update(order=F('order') - 1)


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
        return user.get_profile().own_radio

    def unlock_all(self):
        self.all().update(computing_next_songs=False)

    def ready_objects(self):
        return self.filter(ready=True, creator__isnull=False, deleted=False, blacklisted=False).select_related('creator', 'creator__userprofile')

    def most_actives(self):
        from yametrics.models import RadioMetricsManager
        rm = RadioMetricsManager()
        results = rm.filter('current_users', limit=5, id_only=True)
        ids = [res['db_id'] for res in results]
        return self.filter(id__in=ids).order_by('-current_connections')

    def most_popular_today(self):
        from yametrics.models import RadioPopularityManager
        rm = RadioPopularityManager()
        results = rm.most_popular(limit=yabase_settings.MOST_ACTIVE_RADIOS_LIMIT, db_only=True)
        ids = [res['db_id'] for res in results]
        return self.filter(id__in=ids)

    def last_indexed(self):
        from yasearch.models import RadiosManager
        rm = RadiosManager()
        doc = rm.last_doc()
        if doc is not None:
            return self.get(id=doc.get('db_id'))
        else:
            return None

    def search_fuzzy(self, search_text, limit=5):
        from yasearch.models import RadiosManager
        rm = RadiosManager()
        return rm.search(query=search_text, limit=limit)

    def delete_fake_radios(self):
        self.filter(name__startswith='____fake____').delete()

    def generate_fake_radios(self, count, song_count):
        for _i in range(0, count):
            radio_uuid = uuid.uuid4().hex
            name = '____fake____%s' % radio_uuid
            radio = Radio(name=name, ready=True, uuid=str(radio_uuid), creator=User.objects.all().order_by('?')[0])
            radio.save()
            playlist, _created = radio.get_or_create_default_playlist()
            metadatas = SongMetadata.objects.filter(yasound_song_id__isnull=False).order_by('?')[:song_count]
            for metadata in metadatas:
                song_instance = SongInstance(metadata=metadata, playlist=playlist)
                song_instance.save()
        logger.info('%d fake radios generated with %d songs' % (count, song_count))

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

    def clean_tags(self):
        qs = self.all()
        logger.info('cleaning radio tags')
        for radio in qs:
            tags = radio.tags.all()
            to_remove = []
            to_add = []
            for tag in tags:
                cleaned_tag = clean_tag(tag.name)
                if len(cleaned_tag) == 0:
                    logger.info('removing "%s" from radio "%s"' % (tag.name, unicode(radio)))
                    to_remove.append(tag.name)
                    continue

                if cleaned_tag != tag.name:
                    logger.info('"%s" --> "%s" for radio "%s"' % (tag.name, cleaned_tag, unicode(radio)))
                    to_remove.append(tag.name)
                    to_add.append(cleaned_tag)
            radio.tags.remove(*to_remove)
            radio.tags.add(*to_add)
        logger.info('done')

    def delete_radio(self, radio):
        radio.empty_next_songs_queue()
        radio.delete()

    def uuid_from_id(self, radio_id):
        """Convienient function to get uuid from id (data is cached)"""

        radio_uuid = None
        cache_key = 'radio_%s.uuid' % (radio_id)
        radio_uuid = cache.get(cache_key)
        if not radio_uuid:
            qs = self.filter(id=radio_id).values_list('uuid', flat=True)
            if len(qs) > 0:
                radio_uuid = qs[0]
                cache.set(cache_key, radio_uuid)
        return radio_uuid

class Radio(models.Model):
    objects = RadioManager()
    creator = models.ForeignKey(User, verbose_name=_('creator'), related_name='owned_radios', null=True, blank=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    ready = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, blank=True)
    picture = models.ImageField(_('picture'), upload_to=yaapp_settings.RADIO_PICTURE_FOLDER, null=True, blank=True)
    url = models.CharField(_('url'), null=True, blank=True, max_length=200)
    uuid = models.CharField(_('uuid'), max_length=48, blank=True)
    description = models.TextField(_('description'), blank=True)
    genre = models.CharField(_('genre'), max_length=255, blank=True, choices=yabase_settings.RADIO_STYLE_CHOICES, default=yabase_settings.RADIO_STYLE_ALL)
    theme = models.CharField(_('theme'), max_length=255, blank=True)
    tags = TaggableManager(_('tags'), blank=True)
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
    new_wall_messages_count = models.IntegerField(default=0)  # number of new messages since last creator visit
    popularity_score = models.IntegerField(default=0)  # updated by yametrics.RadioPopularityManager.compute_progression
    origin = models.SmallIntegerField(_('radio origin'), choices=yabase_settings.RADIO_ORIGIN_CHOICES, default=yabase_settings.RADIO_ORIGIN_YASOUND)
    country = models.ForeignKey(Country, verbose_name=_('country'), null=True, blank=True)
    city = models.CharField(_('city'), max_length=128, blank=True)
    latitude = models.FloatField(null=True, blank=True) # degrees
    longitude = models.FloatField(null=True, blank=True) # degrees
    blacklisted = models.BooleanField(_('blacklisted'), default=False)

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

    def mark_as_deleted(self):
        if not self.deleted:
            self.deleted = True
            self.save()
            yabase_signals.radio_deleted.send(sender=self, radio=self)

    def save(self, *args, **kwargs):
        metadata_updated = False
        ready_changed = False

        if not self.pk:
            # creation
            self.leaderboard_rank = Radio.objects.count()

            metadata_updated = True
            ready_changed = True
        else:
            saved = Radio.objects.get(pk=self.pk)

            name_changed = self.name != saved.name
            genre_changed = self.genre != saved.genre

            deleted_changed = self.deleted != saved.deleted
            ready_changed = self.ready != saved.ready
            description_changed = self.description != saved.description

            metadata_updated = name_changed or genre_changed or deleted_changed or ready_changed or description_changed

        if not self.uuid:
            self.uuid = uuid.uuid4().hex

        super(Radio, self).save(*args, **kwargs)

        if ready_changed and self.ready:
            self.now_ready()

        if metadata_updated:
            yabase_signals.radio_metadata_updated.send(sender=self, radio=self)

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
        songs_queryset = SongInstance.objects.filter(playlist__radio=self, metadata__yasound_song_id__gt=0, enabled=True).exclude(last_play_time__gt=time_limit).exclude(id__in=next_songs).order_by('last_play_time')
        if self.current_song:
            songs_queryset = songs_queryset.exclude(id=self.current_song.id)

        count = songs_queryset.count()

        if count == 0:
            songs_queryset = SongInstance.objects.filter(playlist__radio=self, metadata__yasound_song_id__gt=0, enabled=True).exclude(id__in=next_songs).order_by('last_play_time') # try without time limit
            if self.current_song:
                songs_queryset = songs_queryset.exclude(id=self.current_song.id)
            count = songs_queryset.count()

        if count == 0:
            songs_queryset = SongInstance.objects.filter(playlist__radio=self, metadata__yasound_song_id__gt=0, enabled=True).order_by('last_play_time') # try including current song and next songs
            count = songs_queryset.count()

        if count == 0:
            print 'no available songs'
            return None

        frequencies = songs_queryset.values_list('frequency', flat=True)
        # use frequency * frequency to have high frequencies very different from low frequencies
        # multiply frequency weight by a date factor to have higher probabilities for songs not played since a long time (date factor = 1 for older song, 1 for more recent one)
        first_idx_factor = 10
        last_idx_factor = 0.001
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
        self.set_current_song(song)
        self.save()
        self.fill_next_songs_queue()

        return song # SongInstance

    def set_current_song(self, song_instance, play_date=None):
        if play_date is None:
            play_date = datetime.datetime.now()

        self.current_song = song_instance
        self.current_song_play_date = play_date

        song_json, song_dict = SongInstance.objects.set_current_song_json(self, song_instance)

        self.save()

        SongInstance.objects.filter(id=song_instance.id).update(play_count=F('play_count') + 1, last_play_time = play_date)

        yabase_signals.new_current_song.send(sender=self, radio=self, song_json=song_json, song=song_instance, song_dict=song_dict)

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
        tags_array = clean_tags(string.split(tags_string, separator))
        self.tags.clear()
        for tag in tags_array:
            self.tags.add(tag)
        yabase_signals.radio_metadata_updated.send(sender=self, radio=self)


    def fill_bundle(self, bundle):
        bundle.data['description'] = linebreaks(urlize(self.description))
        bundle.data['nb_current_users'] = self.nb_current_users
        bundle.data['tags'] = self.tags_to_string()
        bundle.data['stream_url'] = self.stream_url
        bundle.data['m3u_url'] = self.m3u_url
        bundle.data['web_url'] = self.web_url

    def as_dict(self, request_user=None):
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'slug': self.slug,
            'origin': self.origin,
            'name': self.name,
            'favorites': self.favorites,
            'messages': self.message_count,
            'likes': self.like_count,
            'nb_current_users' : self.nb_current_users,
            'tags' : self.tags_to_string(),
            'picture': self.picture_url,
            'large_picture': self.large_picture_url,
            'ready': self.ready,
            'stream_url' : self.stream_url,
            'm3u_url' : self.m3u_url,
            'web_url': self.web_url,
            'genre': self.genre,
            'overall_listening_time': self.overall_listening_time,
            'overall_listening_time_minutes': int(self.overall_listening_time / 60.0),
            'description': self.description,
            'genre':self.genre,
            'theme':self.theme,
            'audience_peak': self.audience_peak,
            'leaderboard_rank': self.leaderboard_rank,
            'leaderboard_favorites': self.leaderboard_favorites,
            'created': self.created,
            'creator': self.creator.get_profile().as_dict(request_user=request_user),
        }
        if request_user == self.creator:
            data['new_wall_messages_count'] = self.new_wall_messages_count
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
        n = user.get_profile().name
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

    def is_favorite(self, user):
        """
        Return true if user has added this radio as a favorite
        """
        if user.is_anonymous():
            return False

        if RadioUser.objects.filter(radio__id=self.id, user=user, favorite=True).count() > 0:
            return True
        return False

    @property
    def message_count(self):
        return WallEvent.objects.get_message_events(self).count()

    @property
    def like_count(self):
        return WallEvent.objects.get_like_events(self).count()

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
        yabase_signals.user_started_listening.send(sender=self, radio=self, user=user)
        yabase_signals.user_started_listening_song.send(sender=self, radio=self, user=user, song=self.current_song)

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

    # listening_duration is the total listening duration for all the clients who were connected to the radio before it stopped
    def stopped_playing(self, listening_duration):
        RadioUser.objects.filter(radio=self, listening=True).update(listening=False)
        self.anonymous_audience = 0
        self.save()
        atomic_inc(self, 'overall_listening_time', listening_duration)

        self.save()

    def song_starts_playing(self, song_instance, play_date=None):
        if play_date == None:
            play_date = datetime.datetime.now()
        # if radio has listeners, the song has been really played, so report it
        #logger.debug('song_starts_playing: %s / %s - %s' % (self.id, self.uuid, song_instance.id))
        if self.current_song and self.nb_current_users > 0:
            task_report_song.delay(self, self.current_song)

        # update current song
        self.set_current_song(song_instance, play_date)

    def user_connection(self, user):
        print 'user %s entered radio %s' % (user.get_profile().name, self.name)
        creator = self.creator
        if not creator:
            return
        creator_profile = creator.get_profile()
        creator_profile.user_in_my_radio(creator_profile, self)

        # reset unread wall messages count
        Radio.objects.filter(id=self.id).update(new_wall_messages_count=0)


    def create_listening_stat(self):
        favorites = RadioUser.objects.get_favorite().filter(radio=self).count()
        likes = RadioUser.objects.get_likers().filter(radio=self).count()
        dislikes = RadioUser.objects.get_dislikers().filter(radio=self).count()
        stat = RadioListeningStat.objects.create(radio=self, overall_listening_time=self.overall_listening_time, audience_peak=self.current_audience_peak, connections=self.current_connections, favorites=favorites, likes=likes, dislikes=dislikes)

        # reset current audience peak
        # reset current number of connections
        audience = self.audience_total
        Radio.objects.filter(id=self.id).update(current_audience_peak=audience, current_connections=0)

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

    def relative_leaderboard_as_dicts(self):
        leaderboard = self.relative_leaderboard()
        data = []
        for i in leaderboard:
            dict = {'id': i.id,
                    'name': i.name,
                    'leaderboard_favorites': i.leaderboard_favorites,
                    'leaderboard_rank': i.leaderboard_rank,
                    'mine': True if i.id == self.id else False
                    }
            data.append(dict)
        return data

    def current_users(self, limit=25, skip=0):
        """returns users (anonymous + authenticated) for the radio

        :return: data, total_count
        """

        users = User.objects.filter(Q(radiouser__connected=True) | Q(radiouser__listening=True), radiouser__radio=self).all()
        total_count = users.count()

        users = users[skip:limit+skip]
        data = []
        for user in users:
            data.append(user.get_profile().as_dict())

        max_anonymous = limit - len(data)
        if max_anonymous > 0:
            from account.models import AnonymousManager, UserProfile
            manager = AnonymousManager()
            anons = manager.anonymous_for_radio(self.uuid)
            if anons is not None:
                total_count += len(anons)
                for i, anon in enumerate(anons):
                    if i > max_anonymous:
                        break
                    anonymous_name = _('Anonymous user')
                    city_record = anon.get('city_record')
                    if city_record is None:
                        city_record = {}
                    city = city_record.get('city')
                    country = city_record.get('country_name')
                    anonymous_user = UserProfile(name=unicode(anonymous_name), city=city)
                    data.append(anonymous_user.as_dict(anonymous_id=anon.get('anonymous_id')))

        return data, total_count

    @property
    def nb_current_users(self):
        """Return the number of (anonymous+authenticated) users """

        nb_users = User.objects.filter(Q(radiouser__connected=True) | Q(radiouser__listening=True), radiouser__radio=self).count()
        nb_anons = 0

        from account.models import AnonymousManager
        manager = AnonymousManager()
        anons = manager.anonymous_for_radio(self.uuid)
        if anons is not None:
            nb_anons = len(anons)
        return nb_users + nb_anons

    @property
    def nb_current_authenticated_users(self):
        """Return the number of authenticated only users """

        nb_users = User.objects.filter(Q(radiouser__connected=True) | Q(radiouser__listening=True), radiouser__radio=self).count()
        return nb_users

    @property
    def audience_total(self):
        audience = self.nb_current_authenticated_users
        audience += self.anonymous_audience
        return audience

    @property
    def unmatched_songs(self):
        songs = SongInstance.objects.filter(metadata__yasound_song_id=None, playlist__in=self.playlists.all())
        return songs

    def fans(self, limit=25, skip=0):
        """returns users (anonymous + authenticated) for the radio

        :return: data, total_count
        """

        users = self.radiouser_set.select_related('user').filter(favorite=True)
        total_count = users.count()

        users = users[skip:limit + skip]
        data = []
        for ru in users:
            data.append(ru.user.get_profile().as_dict())

        return data, total_count

    def get_picture_url(self, size='210x210', crop='center', **kwargs):
        if self.picture:
            try:
                url = get_thumbnail(self.picture,  size, crop=crop, format='JPEG', quality=70, **kwargs).url
            except:
                url = get_thumbnail(yaapp_settings.DEFAULT_IMAGE_PATH, size, crop=crop, **kwargs).url
        else:
            if self.origin == yabase_settings.RADIO_ORIGIN_RADIOWAYS:
                return self.radioways_radio.get_cover_url(size)
            url = get_thumbnail(yaapp_settings.DEFAULT_IMAGE_PATH, size, crop=crop, format='JPEG', quality=70, **kwargs).url
        return url

    @property
    def picture_url(self):
        """return standard radio cover url (210x210)
        """

        return self.get_picture_url(size='210x210')

    @property
    def large_picture_url(self):
        """return large radio cover url (640x640)
        """

        return self.get_picture_url(size='210x210')

    @property
    def small_picture_url(self):
        """return small radio cover url (28x28)
        """

        return self.get_picture_url(size='28x28')

    def set_picture(self, data):
        filename = self.build_picture_filename()
        if self.picture and len(self.picture.name) > 0:
            self.picture.delete(save=True)
        self.picture.save(filename, data, save=True)
        delete(self.picture, delete_file=False) # reset sorl-thumbnail cache since the source file has been replaced
        self.invalidate_wall_layout_cache()

    def invalidate_wall_layout_cache(self):
        key = 'radio_%s.wall_layout' % (self.id)
        cache.delete(key)
        prefs = self.wall_layout_preferences()
        header_prefs = prefs.get('header', {})
        pictures = header_prefs.get('pictures', [])
        if len(pictures) < 8:
            self.update_wall_layout_preferences(prefs)

    def wall_layout_preferences(self, default={}):
        """ return wall_layout preferences object. """
        m = RadioAdditionalInfosManager()
        doc = m.information(self.uuid)
        if doc is None:
            return default
        else:
            return doc.get('wall_layout', {})

    def update_wall_layout_preferences(self, prefs={'header': {}}):
        """ save wall_layout preferences """
        m = RadioAdditionalInfosManager()

        header_prefs = prefs.get('header', {})
        display = header_prefs.get('display', yabase_settings.WALL_HEADER_DISPLAY_RADIO_PICTURE)
        fx = header_prefs.get('fx', yabase_settings.WALL_HEADER_FX_BLUR)
        pictures = []
        if display == yabase_settings.WALL_HEADER_DISPLAY_RADIO_PICTURE:
            gaussianblur = None
            if fx == yabase_settings.WALL_HEADER_FX_BLUR:
                gaussianblur = 20
            pictures = [self.get_picture_url(size='1200x400', gaussianblur=gaussianblur)]

        elif display == yabase_settings.WALL_HEADER_DISPLAY_COVERS:
            song_ids = SongMetadata.objects.filter(songinstance__playlist__radio=self).order_by('?')[:300].values_list('yasound_song_id', flat=True)
            songs = YasoundSong.objects.filter(id__in=list(song_ids), cover_filename__isnull=False).order_by('?')[:8]
            size = '157x157'
            for i, song in enumerate(songs):
                if i > 5:
                    size = '314x314'

                if song.has_cover():
                    pictures.append(song.custom_cover_url(size))

            if len(pictures) != 8:
                # not enough song covers, using fallback based on radio picture
                gaussianblur = None
                if fx == yabase_settings.WALL_HEADER_FX_BLUR:
                    gaussianblur = 20
                pictures = [self.get_picture_url(size='1200x400', gaussianblur=gaussianblur)]

        # save pictures
        if prefs.get('header') is None:
            prefs['header'] = {}

        prefs['header']['pictures'] = pictures

        # save prefs
        m.add_information(self.uuid, 'wall_layout', prefs)

        key = 'radio_%s.wall_layout' % (self.id)
        cache.delete(key)
        return prefs

    @property
    def wall_layout(self):
        """ return a list of pictures urls """
        key = 'radio_%s.wall_layout' % (self.id)
        data = cache.get(key)
        if data:
            return data

        wall_layout_preferences = self.wall_layout_preferences()
        header_prefs = wall_layout_preferences.get('header')
        if header_prefs is None:
            wall_layout_preferences = self.update_wall_layout_preferences()
            header_prefs = wall_layout_preferences.get('header')

        data = header_prefs.get('pictures')
        cache.set(key, data, 60 * 60)
        return data

    def clear_pictures_cache(self):
        """ invalidate pictures cache """
        key = 'radio_%s.pictures' % (self.id)
        cache.delete(key)

    def build_fuzzy_index(self, upsert=False, insert=True):
        from yasearch.models import RadiosManager
        rm = RadiosManager()
        return rm.add_radio(self, upsert, insert)

    def remove_from_fuzzy_index(self):
        from yasearch.models import RadiosManager
        rm = RadiosManager()
        return rm.remove_radio(self)

    def build_picture_filename(self):
        filename = 'radio_%d_picture.png' % self.id
        return filename

    def delete_song_instances(self, ids):
        self.empty_next_songs_queue()

        SongInstance.objects.filter(id__in=ids, playlist__radio=self).delete()

    @property
    def stream_url(self):
        url = self.url
        if url is None or url == '':
            url = yaapp_settings.YASOUND_STREAM_SERVER_URL + self.uuid
        return url

    @property
    def m3u_url(self):
        return absolute_url(reverse('radio_m3u', args=[self.uuid]))

    @property
    def web_url(self):
        url = yaapp_settings.YASOUND_RADIO_WEB_URL + self.uuid
        return url

    @property
    def meta_description(self):
        """ return data useful for <meta name="description"/> tag"""

        if self.description is not None and len(self.description) > 0:
            if self.genre:
                return _('%(description)s (style: %(genre)s) - A webradio powered by YaSound') % {'description': self.description, 'genre': self.get_genre_display().lower()}
            else:
                return _('%(description)s - A webradio powered by YaSound') % {'description': self.description}
        else:
            if self.genre:
                return _('Listen to the online webradio %(name)s (style: %(genre)s) - powered by YaSound') % {'name': self.name, 'genre': self.get_genre_display().lower()}
            else:
                return _('Listen to the online webradio %(name)s - powered by YaSound') % {'name': self.name}

    def added_in_favorites(self, user):
        creator_profile = self.creator.get_profile()
        creator_profile.my_radio_added_in_favorites(user.get_profile(), self)

    def now_ready(self):
        self.creator.get_profile().radio_is_ready(self)
        yabase_signals.new_animator_activity.send(sender=self,
                                                  user=self.creator,
                                                  radio=self,
                                                  atype=yabase_settings.ANIMATOR_TYPE_CREATE_RADIO)
        if self.ready:
            yabase_signals.radio_is_ready.send(sender=self, radio=self)

    def shared(self, user, share_type=None):
        yabase_signals.radio_shared.send(sender=self, radio=self, user=user, share_type=share_type)
        self.creator.get_profile().my_radio_shared(user.get_profile(), self)

    def post_message(self, user, message):
        WallEvent.objects.add_post_message_event(radio=self, user=user, message=message)

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

    def set_live(self, enabled=False, name=None, album=None, artist=None, id=None):
        key = 'radio_%s.live' % (str(self.id))
        current_song_key = 'radio_%s.current_song.json' % (str(self.id))
        cache.delete(current_song_key)
        if not enabled:
            cache.delete(key)
        else:
            sm = SongMetadata.objects.create(name=name,
                                        album_name=album,
                                        artist_name=artist)
            playlist, _created = self.get_or_create_default_playlist()
            si = SongInstance.objects.create(metadata=sm, playlist=playlist)

            data = {
                'name': name,
                'id': si.id,
                'album': album,
                'artist': artist,
                'cover': '/media/images/on_air.png',
                'large_cover': '/media/images/on_air.png'
            }

            if not self.ready:
                self.ready = True
                self.save()

            cache.set(key, data, 100*60)


    def is_live(self):
        key = 'radio_%s.live' % (str(self.id))
        if cache.get(key) is not None:
            return True
        return False

    def live_data(self):
        key = 'radio_%s.live' % (str(self.id))
        return cache.get(key)

    def reject_song(self, song_instance):
        yasound_song_id = song_instance.metadata.yasound_song_id
        try:
            yasound_song = YasoundSong.objects.get(id=yasound_song_id)
            manager = MatchingErrorsManager()
            manager.song_rejected(yasound_song)
        except YasoundSong.DoesNotExist:
            pass
        song_instance.delete()

    def clear_current_song_json_cache(self):
        key = 'radio_%s.current_song.json' % (str(self.id))
        cache.delete(key)

    def fix_favorites(self):
        self.favorites = RadioUser.objects.filter(radio=self, favorite=True).count()
        self.save()

    def broadcast_message(self, message):
        message = striptags(message)[:800]

        from task import async_radio_broadcast_message
        async_radio_broadcast_message(self, message)

    def similar_radios(self):
        from yarecommendation.models import ClassifiedRadiosManager
        cm = ClassifiedRadiosManager()
        doc = cm.radio_doc(self.id)
        if doc is not None:
            similar_radios = doc.get('similar_radios')
            if similar_radios:
                return Radio.objects.filter(id__in=similar_radios)
        return Radio.objects.none()

    def programming(self, artists=None, albums=None):
        qs = SongInstance.objects.select_related().filter(playlist__radio=self)
        if artists:
            qs = qs.filter(metadata__artist_name__in=artists)

        if albums:
            qs = qs.filter(metadata__album_name__in=albums)
        tracks = qs.values ('id', 'metadata__name', 'metadata__album_name', 'metadata__artist_name').distinct()
        return tracks

    def programming_artists(self):
        qs = SongInstance.objects.select_related().filter(playlist__radio=self).distinct()
        artists = qs.values('metadata__artist_name').distinct()
        return artists

    def programming_albums(self, artists=None):
        qs = SongInstance.objects.select_related().filter(playlist__radio=self)
        if artists:
            qs = qs.filter(metadata__artist_name__in=artists)
        albums = qs.values('metadata__album_name').distinct()
        return albums

    def message_posted_in_wall(self, wall_event):
        if self.creator:
            creator_profile = self.creator.get_profile()
            creator_profile.message_posted_in_my_radio(wall_event)

            # increment new message count if the creator is not in the radio
            creator_profile = self.creator.get_profile()
            if creator_profile.connected_radio is not self:
                Radio.objects.filter(id=self.id).update(new_wall_messages_count=self.new_wall_messages_count+1)

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
    radio_datas = Radio.objects.all().order_by('-favorites').values_list('id', 'favorites')
    current_rank = 0
    count = 0
    last_favorites = None
    for r in radio_datas:
        radio_id = r[0]
        favs = r[1]
        if favs != last_favorites:
            current_rank = count + 1
        Radio.objects.filter(id=radio_id).update(leaderboard_rank=current_rank, leaderboard_favorites=favs)
        count += 1
        last_favorites = favs


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

    def get_like_events(self, radio):
        events = self.get_events(radio, yabase_settings.EVENT_LIKE)
        return events

    def add_current_song_event(self, radio):
        song_events = self.get_song_events(radio).order_by('-start_date').all()
        if not radio.is_live():
            current_song = radio.current_song
            if current_song and (len(song_events) == 0 or current_song.id != song_events[0].song_id):
                s = radio.current_song
                song_event = WallEvent.objects.create(radio=radio, type=yabase_settings.EVENT_SONG, song=s, start_date = radio.current_song_play_date)
        else:
            live_data = radio.live_data()
            if not live_data:
                return

            if len(song_events) == 0 or live_data['name'] != song_events[0].song_name:
                song_name = live_data['name']
                song_artist = live_data['artist']
                song_album = live_data['album']

                song_event = WallEvent.objects.create(radio=radio,
                                                      type=yabase_settings.EVENT_SONG,
                                                      song_name=song_name,
                                                      song_artist=song_artist,
                                                      song_album=song_album,
                                                      start_date=datetime.datetime.now())


    def create_like_event(self, radio, song, user):
        if not radio.is_live():
            self.create(radio=radio, type=yabase_settings.EVENT_LIKE, song=song, user=user)
        else:
            live_data = radio.live_data()
            if not live_data:
                return
            song_name = live_data['name']
            song_artist = live_data['artist']
            song_album = live_data['album']
            self.create(radio=radio,
                        type=yabase_settings.EVENT_LIKE,
                        user=user,
                        song_name=song_name,
                        song_artist=song_artist,
                        song_album=song_album)



    def add_like_event(self, radio, song, user):
        can_add = True

        # we cannot allow consecutive duplicate like event for a song
        previous_likes = self.filter(type=yabase_settings.EVENT_LIKE, radio=radio, user=user).order_by('-start_date')[:1]
        if previous_likes.count() != 0:
            previous = previous_likes[0]

            if not radio.is_live():
                song_id = song.id
                if previous.song_id == song_id:
                    can_add = False
            else:
                live_data = radio.live_data()
                if previous.song_name == live_data['name'] and previous.song_artist == live_data['artist'] and previous.song_album == live_data['album']:
                    can_add = False


        if can_add:
            self.add_current_song_event(radio)
            self.create_like_event(radio, song, user)

    def add_post_message_event(self, radio, user, message):
        self.add_current_song_event(radio)
        self.create(radio=radio,
            start_date=datetime.datetime.now(),
            type=yabase_settings.EVENT_MESSAGE,
            user=user,
            text=message)

    def likes_for_user(self, user):
        return self.filter(user=user, type=yabase_settings.EVENT_LIKE)

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
            s = '%s - %s - %s' % (self.song_name, self.song_artist, self.song_album)
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
                self.user_name = self.user.get_profile().name
                self.user_picture = self.user.get_profile().picture
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
                self.radio.message_posted_in_wall(self)

            yabase_signals.new_wall_event.send(sender=self, wall_event=self)

    def report_as_abuse(self, user):
        from emailconfirmation.models import EmailTemplate
        context = {
            "user": user,
            "message": self,
        }
        subject, message = EmailTemplate.objects.generate_mail(EmailTemplate.EMAIL_TYPE_ABUSE, context)
        subject = "".join(subject.splitlines())
        send_mail(subject, message, yaapp_settings.DEFAULT_FROM_EMAIL, [a[1] for a in yaapp_settings.MODERATORS])

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

    def user_large_picture_url(self):
        if self.user_picture:
            try:
                url = get_thumbnail(self.user_picture, '640x640', crop='center').url
            except:
                url = yaapp_settings.DEFAULT_IMAGE
        else:
            url = yaapp_settings.DEFAULT_IMAGE
        return url

    @property
    def song_cover_url(self):
        if self.song_cover_filename:
            return YasoundSong.objects.get_cover_url(self.song_cover_filename)
        return '/media/images/default_album.jpg'



    @property
    def song_large_cover_url(self):
        if self.song_cover_filename:
            return YasoundSong.objects.get_cover_url(self.song_cover_filename, size='210x210')
        return '/media/images/default_album.jpg'



    @property
    def username(self):
        if self.user:
            return self.user.username
        return None

    @property
    def radio_uuid(self):
        return self.radio.uuid

    def as_dict(self):
        data = {
            'id': self.id,
            'user_id': self.user.id if self.user is not None else None,
            'user_name': self.user_name,
            'user_username': self.user.username if self.user is not None else None,
            'user_picture': self.user_picture_url,
            'radio_id': self.radio.id,
            'radio_uuid': self.radio.uuid,
            'song_id': self.song.id if self.song is not None else None,
            'song_name': self.song_name,
            'song_album': self.song_album,
            'song_artist': self.song_artist,
            'song_cover_filename': self.song_cover_filename,
            'song_cover_url': self.song_cover_url,
            'song_large_cover_url': self.song_large_cover_url,
            'start_date': self.start_date,
            'text': self.text,
            'type': self.type,
        }
        return data

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


class FeaturedContent(models.Model):
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    activated = models.BooleanField(_('activated'), default=False)
    ftype = models.CharField(max_length=1, choices=yabase_settings.FEATURED_CHOICES, default=yabase_settings.FEATURED_SELECTION)
    radios = models.ManyToManyField(Radio, through='FeaturedRadio', blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.activated:
            FeaturedContent.objects.filter(ftype=self.ftype).exclude(id=self.id).update(activated=False)
        super(FeaturedContent, self).save(*args, **kwargs)

    class Meta:
        db_name = u'default'
        verbose_name = _('featured content')

class FeaturedRadio(models.Model):
    featured_content = models.ForeignKey(FeaturedContent, verbose_name=_('featured content'))
    radio = models.ForeignKey(Radio, verbose_name=_('radio'))
    order = models.IntegerField(_('order'), default=0)
    picture = models.ImageField(upload_to=yaapp_settings.PICTURE_FOLDER, null=True, blank=True)

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


class AnnouncementManager(models.Manager):
    def get_current_announcement(self):
        try:
            return self.filter(activated=True).order_by('-created')[0]
        except:
            return None


class Announcement(models.Model):
    """ A model to store announcements displayed on web app """

    __metaclass__ = TransMeta
    objects = AnnouncementManager()

    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    activated = models.BooleanField(default=False)
    name = models.CharField(_('name'), max_length=255)
    body = models.TextField(_('body'), max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if self.activated:
            Announcement.objects.all().exclude(id=self.id).update(activated=False)
        super(Announcement, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = _('announcement')
        translate = ('name', 'body')


class RadioAdditionalInfosManager():
    """Store additional informations about radios (like wall preferences for instance)."""

    def __init__(self):
        self.db = yaapp_settings.MONGO_DB
        self.collection = self.db.yabase.radios
        self.collection.ensure_index('db_id', unique=True)

    def erase_informations(self):
        self.collection.drop()

    def add_information(self, radio_uuid, information_key, data):
        self.collection.update({'db_id': radio_uuid}, {'$set': {information_key: data}}, upsert=True, safe=True)

    def remove_information(self, user_id, information_key):
        self.collection.update({'db_id': user_id}, {'$unset': {information_key: 1}}, upsert=True, safe=True)

    def information(self, radio_uuid):
        return self.collection.find_one({'db_id': radio_uuid})

    def remove_user(self, radio_uuid):
        self.collection.remove({'db_id': radio_uuid})


def new_current_song_handler(sender, radio, song_json, song, song_dict, **kwargs):
    from yabase.task import async_dispatch_user_started_listening_song
    async_dispatch_user_started_listening_song.delay(radio, song)


def song_metadata_updated(sender, instance, created, **kwargs):
    if instance.yasound_song_id is not None:
        from yaref.task import async_convert_song
        async_convert_song.delay(instance.yasound_song_id, exclude_primary=True)

def animator_activity_handler(sender, user, radio, atype, details=None, playlist=None, **kwargs):
    radio.clear_pictures_cache()

def install_handlers():
    signals.pre_delete.connect(song_instance_deleted, sender=SongInstance)
    signals.post_delete.connect(next_song_deleted, sender=NextSong)
    yabase_signals.new_current_song.connect(new_current_song_handler)
    yabase_signals.new_animator_activity.connect(animator_activity_handler)

    if not yaapp_settings.TEST_MODE:
        signals.post_save.connect(song_metadata_updated, sender=SongMetadata)
install_handlers()


if yaapp_settings.ENABLE_PUSH:
    from push import install_handlers
    install_handlers()
