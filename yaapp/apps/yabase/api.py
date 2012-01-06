from tastypie import fields
from tastypie.resources import ModelResource
from yabase.models import SongMetadata, SongInstance, Playlist, Radio, WallEvent, NextSong, RadioUser
from django.contrib.auth.models import User
from django.conf.urls.defaults import url
from django.shortcuts import get_object_or_404
from tastypie.utils import trailing_slash
import datetime
from tastypie.authentication import Authentication
from tastypie.authorization import DjangoAuthorization, Authorization
import settings as yabase_settings
from account.api import UserResource
from tastypie.authentication import ApiKeyAuthentication 
from tastypie.resources import ModelResource, ALL
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404


class SongMetadataResource(ModelResource):
    class Meta:
        queryset = SongMetadata.objects.all()
        resource_name = 'metadata'
        fields = ['name', 'artist_name', 'album_name', 'track_index', 'track_count', 'disc_index', 'disc_count', 'bpm', 'date', 'score', 'duration', 'genre', 'picture']
        include_resource_uri = False
        authorization= Authorization()
        authentication = Authentication()

class SongInstanceResource(ModelResource):
    metadata = fields.ForeignKey(SongMetadataResource, 'metadata', full=True)
    playlist = fields.ForeignKey('yabase.api.PlaylistResource', 'playlist', full=False)
    class Meta:
        queryset = SongInstance.objects.all()
        resource_name = 'song'
        fields = ['playlist', 'song', 'play_count', 'last_play_time', 'yasound_score', 'metadata']
        include_resource_uri = False

class PlaylistResource(ModelResource):
    class Meta:
        queryset = Playlist.objects.all()
        resource_name = 'playlist'
        fields = ['name', 'source', 'enabled', 'sync_date', 'CRC']
        include_resource_uri = False







class RadioResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=False)
    creator = fields.ForeignKey('yabase.api.UserResource', 'creator', full=True)
    
    # likers ?
    
    class Meta:
        queryset = Radio.objects.all()
        resource_name = 'radio'
        fields = ['id', 'name', 'creator', 'description', 'genre', 'theme', 'url', 'playlists', 'picture', 'tags', 'audience_peak', 'overall_listening_time', 'created']
        include_resource_uri = False;
#        authentication = ApiKeyAuthentication()
        authentication = Authentication()
        authorization = Authorization()
        allowed_methods = ['get', 'post', 'put']
        filtering = {
            'creator': ALL,
            'genre': ALL,
            'name': ('contains',),
        }
        ordering = [
            'overall_listening_time',
            'created',
        ]
        
    def obj_update(self, bundle, request=None, **kwargs):
        radio_resource = super(RadioResource, self).obj_update(bundle, request, **kwargs)
        
        # auto binding seems to work for CharField and FloatField but not for textField and URLField in this case
        radio = radio_resource.obj
        radio.update_with_data(radio_resource.data)
        return radio_resource
        

    def dehydrate(self, bundle):
        radioID = bundle.data['id'];
        radio = Radio.objects.get(pk=radioID)
        radio.fill_bundle(bundle)
        return bundle
    
    
class SelectedRadioResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=False)
    creator = fields.ForeignKey('yabase.api.UserResource', 'creator', full=True)
    
    class Meta:
        queryset = Radio.objects.all()
        resource_name = 'selected_radio'
        fields = ['id', 'name', 'creator', 'description', 'genre', 'theme', 'url', 'playlists', 'picture', 'tags', 'audience_peak', 'overall_listening_time', 'created']
        include_resource_uri = False;
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        allowed_methods = ['get']
        filtering = {
            'genre': ALL,
        }        

    def dehydrate(self, bundle):
        radioID = bundle.data['id'];
        radio = Radio.objects.get(pk=radioID)
        radio.fill_bundle(bundle)
        return bundle
    
    def apply_authorization_limits(self, request, object_list):
        user = request.user
        return object_list.filter(radiouser__user=user, radiouser__radio_selected=True)
    
class FavoriteRadioResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=False)
    creator = fields.ForeignKey('yabase.api.UserResource', 'creator', full=True)
    
    class Meta:
        queryset = Radio.objects.all()
        resource_name = 'favorite_radio'
        fields = ['id', 'name', 'creator', 'description', 'genre', 'theme', 'url', 'playlists', 'picture', 'tags', 'audience_peak', 'overall_listening_time', 'created']
        include_resource_uri = False;
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        allowed_methods = ['get']
        filtering = {
            'genre': ALL,
        }        

    def dehydrate(self, bundle):
        radioID = bundle.data['id'];
        radio = Radio.objects.get(pk=radioID)
        radio.fill_bundle(bundle)
        return bundle
    
    def apply_authorization_limits(self, request, object_list):
        user = request.user
        return object_list.filter(radiouser__user=user, radiouser__favorite=True)

class FriendRadioResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=False)
    creator = fields.ForeignKey('yabase.api.UserResource', 'creator', full=True)
    
    class Meta:
        queryset = Radio.objects.all()
        resource_name = 'friend_radio'
        fields = ['id', 'name', 'creator', 'description', 'genre', 'theme', 'url', 'playlists', 'picture', 'tags', 'audience_peak', 'overall_listening_time', 'created']
        include_resource_uri = False;
        authentication = ApiKeyAuthentication()
        authorization = Authorization()
        allowed_methods = ['get']
        filtering = {
            'genre': ALL,
        }        

    def dehydrate(self, bundle):
        radioID = bundle.data['id'];
        radio = Radio.objects.get(pk=radioID)
        radio.fill_bundle(bundle)
        return bundle
    
    def apply_authorization_limits(self, request, object_list):
        user = request.user
        return object_list.filter(creator__in=user.userprofile.friends.all())


class WallEventResource(ModelResource):
    radio = fields.ForeignKey(RadioResource, 'radio', full=True)
    song = fields.ForeignKey(SongInstanceResource, 'song', full=True, null=True)
    user = fields.ForeignKey(UserResource, 'user', full=True, null=True)
    class Meta:
        queryset = WallEvent.objects.all()
        resource_name = 'wall_event'
        fields = ['id', 'type', 'start_date', 'end_date', 'song', 'old_id', 'user', 'text', 'animated_emoticon', 'picture', 'radio']
        include_resource_uri = False
        authorization= Authorization()
        authentication = Authentication()
        allowed_methods = ['get', 'post']
    
    def obj_create(self, bundle, request=None, **kwargs):
        wall_event_resource = super(WallEventResource, self).obj_create(bundle, request, **kwargs)
        wall_event = wall_event_resource.obj
        if wall_event.type == yabase_settings.EVENT_JOINED:
            print 'joined'
            user = wall_event.user
            radio = wall_event.radio
            radiouser, created = RadioUser.objects.get_or_create(user=user, radio=radio)
            radiouser.connected = True
            radiouser.save()
            
            connected_users = RadioUser.objects.filter(radio=radio, connected=True)
            audience = len(connected_users)
            if audience > radio.audience_peak:
                radio.audience_peak = audience
                radio.save()
            
        elif wall_event.type == yabase_settings.EVENT_LEFT:
            print 'left'
            user = wall_event.user
            radio = wall_event.radio
            radiouser, created = RadioUser.objects.get_or_create(user=user, radio=radio)
            radiouser.connected = False
            radiouser.save()
            
            last_joined = WallEvent.objects.filter(user=user, radio=radio, type=yabase_settings.EVENT_JOINED).order_by('-start_date')[0]
            last_left = WallEvent.objects.filter(user=user, radio=radio, type=yabase_settings.EVENT_LEFT).order_by('-start_date')[0]
            duration = last_left.start_date - last_joined.start_date
            seconds = duration.total_seconds()
            radio.overall_listening_time += seconds
            print 'add %d seconds' % seconds
            radio.save()

class RadioWallEventResource(ModelResource):
    radio = fields.ForeignKey(RadioResource, 'radio', full=True)
    song = fields.ForeignKey(SongInstanceResource, 'song', full=True, null=True)
    user = fields.ForeignKey(UserResource, 'user', full=True, null=True)
    class Meta:
        queryset = WallEvent.objects.all().order_by('-start_date')
        resource_name = 'wall'
        fields = ['id', 'type', 'start_date', 'end_date', 'song', 'old_id', 'user', 'text', 'animated_emoticon', 'picture', 'radio']
        include_resource_uri = False
        filtering = {
            'radio': 'exact',
        }

    def dispatch(self, request_type, request, **kwargs):
        radio = kwargs.pop('radio')
        kwargs['radio'] = get_object_or_404(Radio, id=radio)
        return super(RadioWallEventResource, self).dispatch(request_type, request, **kwargs)


class NextSongsResource(ModelResource):
    song = fields.ForeignKey(SongInstanceResource, 'song', full=True)
    radio = fields.ForeignKey(RadioResource, 'radio', full=True)
    class Meta:
        queryset = NextSong.objects.all()
        resource_name = 'next_songs'
        fields = ['radio', 'song', 'order']
        include_resource_uri = False
        filtering = {
            'radio': 'exact',
        }

    def dispatch(self, request_type, request, **kwargs):
        radio = kwargs.pop('radio')
        kwargs['radio'] = get_object_or_404(Radio, id=radio)
        return super(NextSongsResource, self).dispatch(request_type, request, **kwargs)




class RadioLikerResource(ModelResource):    
    radio = None
    
    class Meta:
        queryset = User.objects.all()
        resource_name = 'likes'
        fields = ['username']
        include_resource_uri = False
    
    def dispatch(self, request_type, request, **kwargs):
        radioID = kwargs.pop('radio')
        self.radio = get_object_or_404(Radio, id=radioID)
        return super(RadioLikerResource, self).dispatch(request_type, request, **kwargs)
    
    def get_object_list(self, request):
        return super(RadioLikerResource, self).get_object_list(request).filter(radiouser__radio=self.radio, radiouser__mood=yabase_settings.MOOD_LIKE)


class RadioUserConnectedResource(ModelResource):    
    radio = None
    
    class Meta:
        queryset = User.objects.all()
        resource_name = 'connected_users'
        fields = ['username']
        include_resource_uri = False
    
    def dispatch(self, request_type, request, **kwargs):
        radioID = kwargs.pop('radio')
        self.radio = get_object_or_404(Radio, id=radioID)
        return super(RadioUserConnectedResource, self).dispatch(request_type, request, **kwargs)
    
    def get_object_list(self, request):
        return super(RadioUserConnectedResource, self).get_object_list(request).filter(radiouser__radio=self.radio, radiouser__connected=True)





class PlayedSongResource(ModelResource):
    radio = fields.ForeignKey(RadioResource, 'radio', full=True)
    song = fields.ForeignKey(SongInstanceResource, 'song', null=True, full=True)

    class Meta:
        queryset = WallEvent.objects.filter(type=yabase_settings.EVENT_SONG).order_by('-start_date')
        resource_name = 'songs'
        fields = ['id', 'start_date', 'end_date', 'radio', 'song']
        include_resource_uri = False
        filtering = {
            'radio': 'exact',
    }
    
    def dispatch(self, request_type, request, **kwargs):
        radio = kwargs.pop('radio')
        kwargs['radio'] = get_object_or_404(Radio, id=radio)
        return super(PlayedSongResource, self).dispatch(request_type, request, **kwargs)

   



