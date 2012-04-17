from account.api import UserResource, YasoundApiKeyAuthentication
from django.conf.urls.defaults import url
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from tastypie import fields, http
from tastypie.authentication import ApiKeyAuthentication, Authentication
from tastypie.authorization import DjangoAuthorization, Authorization, \
    ReadOnlyAuthorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import ModelResource, ModelResource, ALL
from tastypie.utils import trailing_slash
from yabase.models import SongMetadata, SongInstance, Playlist, Radio, WallEvent, \
    NextSong, RadioUser, SongUser, FeaturedRadio
from yaref.models import YasoundSong
from yasearch.models import search_radio, search_radio_by_user, \
    search_radio_by_song
import datetime
import json
import settings as yabase_settings

class SongMetadataResource(ModelResource):
    class Meta:
        queryset = SongMetadata.objects.all()
        resource_name = 'metadata'
        fields = ['name', 'yasound_song_id', 'artist_name', 'album_name', 'track_index', 'track_count', 'disc_index', 'disc_count', 'bpm', 'date', 'score', 'duration', 'genre', 'picture']
        include_resource_uri = False
        authorization= ReadOnlyAuthorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = []

class SongInstanceResource(ModelResource):
    metadata = fields.ForeignKey(SongMetadataResource, 'metadata', full=True)
    playlist = fields.ForeignKey('yabase.api.PlaylistResource', 'playlist', full=False)
    class Meta:
        queryset = SongInstance.objects.all()
        resource_name = 'song'
        fields = ['id', 
                  'playlist', 
                  'play_count', 
                  'last_play_time', 
                  'yasound_score', 
                  'metadata',
                  'need_sync',
                  'likes',
                  'dislikes']
        include_resource_uri = False
        filtering = {
            'playlist': ALL,
        }
        authorization= ReadOnlyAuthorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = ['post', 'get']
        
    def dehydrate(self, bundle):
        song = bundle.obj
        song.fill_bundle(bundle)
        return bundle

class PlaylistResource(ModelResource):
    class Meta:
        queryset = Playlist.objects.all()
        resource_name = 'playlist'
        fields = ['id', 'name',]
        include_resource_uri = False
        authorization= ReadOnlyAuthorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = []




class RadioAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        return True

    def apply_limits(self, request, object_list):
        if request.method != 'GET':
            return object_list.filter(creator=request.user)
        return object_list

class RadioResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=False)
    creator = fields.ForeignKey('yabase.api.UserResource', 'creator', null=True , full=True)
    picture = fields.CharField(attribute='picture_url', default=None, readonly=True)
    
    class Meta:
        queryset = Radio.objects.filter(creator__isnull=False)
        resource_name = 'radio'
        fields = ['id', 'name', 'creator', 'description', 'genre', 'theme', 'uuid', 'playlists', 'tags', 'favorites', 'audience_peak', 'overall_listening_time', 'created', 'ready']
        include_resource_uri = False;
        authentication = YasoundApiKeyAuthentication()
        authorization = RadioAuthorization()
        allowed_methods = ['get', 'put']
        filtering = {
            'creator': ALL,
            'genre': ALL,
            'name': ('contains',),
            'ready': ('exact',),
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

    def apply_sorting(self, obj_list, options=None):
        if 'overall_listening_time' in options.get('order_by', ''):
            # the top radio listing is limited to 25
            return super(RadioResource, self).apply_sorting(obj_list=obj_list, options=options)[:25]
        return super(RadioResource, self).apply_sorting(obj_list=obj_list, options=options)

    def dehydrate(self, bundle):
        radioID = bundle.data['id'];
        radio = Radio.objects.get(pk=radioID)
        radio.fill_bundle(bundle)
        return bundle

class PublicRadioResource(ModelResource):
    creator = fields.ForeignKey('yabase.api.UserResource', 'creator', null=True , full=True)
    picture = fields.CharField(attribute='picture_url', default=None, readonly=True)
    
    class Meta:
        queryset = Radio.objects.filter(creator__isnull=False)
        resource_name = 'public_radio'
        fields = ['id', 'name', 'creator', 'description', 'genre', 'theme', 'uuid', 'tags', ]
        include_resource_uri = False;
        authorization = ReadOnlyAuthorization()
        filtering = {
            'creator': ALL,
            'genre': ALL,
            'name': ('contains',),
            'ready': ('exact',),
        }
        
    def dehydrate(self, bundle):
        radioID = bundle.data['id'];
        radio = Radio.objects.get(pk=radioID)
        radio.fill_bundle(bundle)
        return bundle
    

class SearchRadioResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=False)
    creator = fields.ForeignKey('yabase.api.UserResource', 'creator', full=True)
    picture = fields.CharField(attribute='picture_url', default=None, readonly=True)
    
    class Meta:
        queryset = Radio.objects.ready_objects()
        resource_name = 'search_radio'
        fields = ['id', 'name', 'creator', 'description', 'genre', 'theme', 'uuid', 'playlists', 'tags', 'favorites', 'audience_peak', 'overall_listening_time', 'created', 'ready']
        include_resource_uri = False;
        authentication = YasoundApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        allowed_methods = ['get']
        filtering = {
            'genre': ALL,
        }        

    def dehydrate(self, bundle):
        radioID = bundle.data['id'];
        radio = Radio.objects.get(pk=radioID)
        radio.fill_bundle(bundle)
        return bundle
    
    def get_object_list(self, request):
        search = request.GET.get('search', None)
        obj_list = super(SearchRadioResource, self).get_object_list(request)
        if search:
            # apply search
            obj_list = search_radio(search)
        return obj_list
    
    def obj_get_list(self, request=None, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(request)
    
class SearchRadioByUserResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=False)
    creator = fields.ForeignKey('yabase.api.UserResource', 'creator', null=True, full=True)
    picture = fields.CharField(attribute='picture_url', default=None, readonly=True)
    
    class Meta:
        queryset = Radio.objects.ready_objects()
        resource_name = 'search_radio_by_user'
        fields = ['id', 'name', 'creator', 'description', 'genre', 'theme', 'uuid', 'playlists', 'tags', 'favorites', 'audience_peak', 'overall_listening_time', 'created', 'ready']
        include_resource_uri = False;
        authentication = YasoundApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        allowed_methods = ['get']

    def dehydrate(self, bundle):
        radioID = bundle.data['id'];
        radio = Radio.objects.get(pk=radioID)
        radio.fill_bundle(bundle)
        return bundle
    
    def get_object_list(self, request):
        search = request.GET.get('search', None)
        obj_list = super(SearchRadioByUserResource, self).get_object_list(request)
        if search:
            # apply search
            obj_list = search_radio_by_user(search)
        return obj_list
    
    def obj_get_list(self, request=None, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(request)
    
class SearchRadioBySongResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=False)
    creator = fields.ForeignKey('yabase.api.UserResource', 'creator', null=True, full=True)
    picture = fields.CharField(attribute='picture_url', default=None, readonly=True)

    class Meta:
        queryset = Radio.objects.ready_objects()
        resource_name = 'search_radio_by_song'
        fields = ['id', 'name', 'creator', 'description', 'genre', 'theme', 'uuid', 'playlists', 'tags', 'favorites', 'audience_peak', 'overall_listening_time', 'created', 'ready']
        include_resource_uri = False;
        authentication = YasoundApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        allowed_methods = ['get']

    def dehydrate(self, bundle):
        radioID = bundle.data['id'];
        radio = Radio.objects.get(pk=radioID)
        radio.fill_bundle(bundle)
        return bundle
    
    def get_object_list(self, request):
        search = request.GET.get('search', None)
        obj_list = super(SearchRadioBySongResource, self).get_object_list(request)
        if search:
            # apply search
            obj_list = search_radio_by_song(search)
        return obj_list
    
    def obj_get_list(self, request=None, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(request)
    
class SelectedRadioResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=False)
    creator = fields.ForeignKey('yabase.api.UserResource', 'creator', null=True, full=True)
    picture = fields.CharField(attribute='picture_url', default=None, readonly=True)
    
    class Meta:
        queryset = Radio.objects.ready_objects()
        resource_name = 'selected_radio'
        fields = ['id', 'name', 'creator', 'description', 'genre', 'theme', 'uuid', 'playlists', 'tags', 'favorites', 'audience_peak', 'overall_listening_time', 'created', 'ready']
        include_resource_uri = False;
        authentication = YasoundApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        allowed_methods = ['get']
        filtering = {
            'genre': ALL,
            'ready': ('exact',),
        }        

    def dehydrate(self, bundle):
        radioID = bundle.data['id'];
        radio = Radio.objects.get(pk=radioID)
        radio.fill_bundle(bundle)
        return bundle
    
    
    def get_object_list(self, request):
        obj_list = super(SelectedRadioResource, self).get_object_list(request).filter(featuredcontent__activated=True).order_by('featuredradio__order')
        return obj_list
    
class TopRadioResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=False)
    creator = fields.ForeignKey('yabase.api.UserResource', 'creator', null=True, full=True)
    picture = fields.CharField(attribute='picture_url', default=None, readonly=True)
    
    class Meta:
        queryset = Radio.objects.ready_objects()
        resource_name = 'top_radio'
        fields = ['id', 'name', 'creator', 'description', 'genre', 'theme', 'uuid', 'playlists', 'tags', 'favorites', 'audience_peak', 'overall_listening_time', 'created', 'ready']
        include_resource_uri = False;
        authentication = YasoundApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        allowed_methods = ['get']
        filtering = {
            'genre': ALL,
            'ready': ('exact',),
        }        

    def dehydrate(self, bundle):
        radioID = bundle.data['id'];
        radio = Radio.objects.get(pk=radioID)
        radio.fill_bundle(bundle)
        return bundle
    
    def apply_sorting(self, obj_list, options=None):
        return super(TopRadioResource, self).apply_sorting(obj_list=obj_list, options=options)[:yabase_settings.TOP_RADIOS_LIMIT]
    
    def get_object_list(self, request):
        radios = super(TopRadioResource, self).get_object_list(request).order_by('-favorites')
        return radios

class FavoriteRadioResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=False)
    creator = fields.ForeignKey('yabase.api.UserResource', 'creator', null=True, full=True)
    picture = fields.CharField(attribute='picture_url', default=None, readonly=True)
    
    class Meta:
        queryset = Radio.objects.ready_objects()
        resource_name = 'favorite_radio'
        fields = ['id', 'name', 'creator', 'description', 'genre', 'theme', 'uuid', 'playlists', 'tags', 'favorites', 'audience_peak', 'overall_listening_time', 'created', 'ready']
        include_resource_uri = False;
        authentication = YasoundApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        allowed_methods = ['get']
        filtering = {
            'genre': ALL,
            'ready': ('exact',),
        }        

    def dehydrate(self, bundle):
        radioID = bundle.data['id'];
        radio = Radio.objects.get(pk=radioID)
        radio.fill_bundle(bundle)
        return bundle
    
    def apply_authorization_limits(self, request, object_list):
        user = request.user
        return object_list.filter(radiouser__user=user, radiouser__favorite=True)

class UserFavoriteRadioResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=False)
    creator = fields.ForeignKey('yabase.api.UserResource', 'creator', null=True, full=True)
    picture = fields.CharField(attribute='picture_url', default=None, readonly=True)
    
    class Meta:
        queryset = Radio.objects.ready_objects()
        resource_name = 'favorite_radio'
        fields = ['id', 'name', 'creator', 'description', 'genre', 'theme', 'uuid', 'playlists', 'tags', 'favorites', 'audience_peak', 'overall_listening_time', 'created', 'ready']
        include_resource_uri = False;
        authentication = YasoundApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        allowed_methods = ['get']
        filtering = {
            'genre': ALL,
            'ready': ('exact',),
        }        

    def dehydrate(self, bundle):
        radioID = bundle.data['id'];
        radio = Radio.objects.get(pk=radioID)
        radio.fill_bundle(bundle)
        return bundle
    
    def obj_get_list(self, request=None, **kwargs):
        user_id = kwargs.pop('user_id')
        return self.get_object_list(request).filter(radiouser__user__id=user_id, radiouser__favorite=True)



class FriendRadioResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=False)
    creator = fields.ForeignKey('yabase.api.UserResource', 'creator', null=True, full=True)
    picture = fields.CharField(attribute='picture_url', default=None, readonly=True)

    class Meta:
        queryset = Radio.objects.ready_objects()
        resource_name = 'friend_radio'
        fields = ['id', 'name', 'creator', 'description', 'genre', 'theme', 'uuid', 'playlists', 'tags', 'favorites', 'audience_peak', 'overall_listening_time', 'created', 'ready']
        include_resource_uri = False;
        authentication = YasoundApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        allowed_methods = ['get']
        filtering = {
            'genre': ALL,
            'ready': ('exact',),
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
    user = fields.ForeignKey(UserResource, 'user', full=True, null=True)
    class Meta:
        queryset = WallEvent.objects.all()
        resource_name = 'wall_event'
        fields = ['id', 'type', 'start_date', 'user', 'text', 'animated_emoticon', 'picture', 'radio']
        include_resource_uri = False
        authorization= Authorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = ['post']
        
    def obj_create(self, bundle, request=None, **kwargs):
        if bundle.data['type'] == yabase_settings.EVENT_SONG:
            print 'cannot post Song messages'
            return None
        
        radio_uri = bundle.data['radio']
        elements = radio_uri.split('/')
        radio_id = int(elements[len(elements)-2])
        try:
            radio = Radio.objects.get(id=radio_id)
        except Radio.DoesNotExist:
            return None
        
        WallEvent.objects.add_current_song_event(radio)

        wall_event_resource = super(WallEventResource, self).obj_create(bundle, request, **kwargs)
        wall_event_resource.obj.start_date = datetime.datetime.now() # be sure the song event is before message event
        wall_event_resource.obj.save()
        return wall_event_resource

class RadioWallEventResource(ModelResource):
    radio = fields.ForeignKey(RadioResource, 'radio', full=False)
#    song = fields.ForeignKey(SongInstanceResource, 'song', full=True, null=True)
#    user = fields.ForeignKey(UserResource, 'user', full=True, null=True)
    class Meta:
        queryset = WallEvent.objects.all().order_by('-start_date')
        resource_name = 'wall'
        fields = ['id', 'type', 'start_date', 'song_name', 'song_artist', 'song_album', 'song_cover_filename', 'user_name', 'user_picture', 'text', 'animated_emoticon', 'picture', 'radio']
        include_resource_uri = False
        authorization = ReadOnlyAuthorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = ['get']
        filtering = {
            'radio': 'exact',
            'id': 'lt,gt',
            }

    def dispatch(self, request_type, request, **kwargs):
        radio = kwargs.pop('radio')
        kwargs['radio'] = get_object_or_404(Radio, id=radio)
        return super(RadioWallEventResource, self).dispatch(request_type, request, **kwargs)
    
    def dehydrate(self, bundle):
        event = bundle.obj
        user_id = None
        song_id = None
        if event.user:
            user_id = event.user.id
        if event.song:
            song_id = event.song.id
        bundle.data['radio_id'] = event.radio.id
        bundle.data['user_id'] = user_id
        bundle.data['song_id'] = song_id
        return bundle


class RadioNextSongsResource(ModelResource):
#    song = fields.ForeignKey(SongInstanceResource, 'song', full=True)
    radio = fields.ForeignKey(RadioResource, 'radio', full=True)
    class Meta:
        queryset = NextSong.objects.order_by('order')
        resource_name = 'next_songs'
        fields = ['id', 'radio', 'order']
        include_resource_uri = False
        authorization= ReadOnlyAuthorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = ['get']
        filtering = {
            'radio': 'exact',
            }

    def dispatch(self, request_type, request, **kwargs):
        radio = kwargs.pop('radio')
        kwargs['radio'] = get_object_or_404(Radio, id=radio)
        return super(RadioNextSongsResource, self).dispatch(request_type, request, **kwargs)
    
    def dehydrate(self, bundle):
        desc_dict = bundle.obj.song.song_description
        bundle.data['song'] = desc_dict
        return bundle

class NextSongResource(ModelResource):
    song = fields.ForeignKey(SongInstanceResource, 'song', full=True)
    radio = fields.ForeignKey(RadioResource, 'radio', full=True)
    class Meta:
        queryset = NextSong.objects.all()
        resource_name = 'next_song'
        fields = ['id', 'radio', 'song', 'order']
        include_resource_uri = False
        authorization= Authorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = ['post', 'put', 'delete']
        
    def obj_delete(self, request=None, **kwargs):
        try:
            obj = self.get_object_list(request).get(**kwargs)
        except ObjectDoesNotExist:
            pass
        
        radio = obj.radio
        super(NextSongResource, self).obj_delete(request, **kwargs)
        radio.fill_next_songs_queue()
        
        


class RadioLikerResource(ModelResource):    
    radio = None
    
    class Meta:
        queryset = User.objects.all()
        resource_name = 'like_user'
        fields = ['id']
        allowed_methods = ['get']
        authorization= ReadOnlyAuthorization()
        authentication = YasoundApiKeyAuthentication()
        include_resource_uri = False
    
    def dispatch(self, request_type, request, **kwargs):
        radioID = kwargs.pop('radio')
        self.radio = get_object_or_404(Radio, id=radioID)
        return super(RadioLikerResource, self).dispatch(request_type, request, **kwargs)
    
    def get_object_list(self, request):
        return super(RadioLikerResource, self).get_object_list(request).filter(radiouser__radio=self.radio, radiouser__mood=yabase_settings.MOOD_LIKE)
    
    def dehydrate(self, bundle):
        bundle.data['username'] = bundle.obj.username
        bundle.obj.userprofile.fill_user_bundle(bundle)
        return bundle
    
class RadioFavoriteResource(ModelResource):    
    radio = None
    
    class Meta:
        queryset = User.objects.all()
        resource_name = 'favorite_user'
        fields = ['id']
        allowed_methods = ['get']
        authorization= ReadOnlyAuthorization()
        authentication = YasoundApiKeyAuthentication()
        include_resource_uri = False
    
    def dispatch(self, request_type, request, **kwargs):
        radioID = kwargs.pop('radio')
        self.radio = get_object_or_404(Radio, id=radioID)
        return super(RadioFavoriteResource, self).dispatch(request_type, request, **kwargs)
    
    def get_object_list(self, request):
        return super(RadioFavoriteResource, self).get_object_list(request).filter(radiouser__radio=self.radio, radiouser__favorite=True)
    
    def dehydrate(self, bundle):
        bundle.data['username'] = bundle.obj.username
        bundle.obj.userprofile.fill_user_bundle(bundle)
        return bundle


class RadioCurrentUserResource(ModelResource):    
    radio = None
    
    class Meta:
        queryset = User.objects.all()
        resource_name = 'current_user'
        fields = ['id']
        authorization= ReadOnlyAuthorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = ['get']
        include_resource_uri = False
    
    def dispatch(self, request_type, request, **kwargs):
        radioID = kwargs.pop('radio')
        self.radio = get_object_or_404(Radio, id=radioID)
        return super(RadioCurrentUserResource, self).dispatch(request_type, request, **kwargs)
    
    def get_object_list(self, request):
        return self.radio.current_users()
    
    def dehydrate(self, bundle):
        bundle.data['username'] = bundle.obj.username
        bundle.obj.userprofile.fill_user_bundle(bundle)
        return bundle
    

class RadioUserResource(ModelResource): 
    radio = fields.ForeignKey(RadioResource, 'radio', full=True)
    user = fields.ForeignKey(UserResource, 'user', full=True)   
    class Meta:
        queryset = RadioUser.objects.all()
        resource_name = 'radio_user'
        fields = ['radio', 'user', 'mood', 'favorite']
        allowed_methods = ['get']
        include_resource_uri = False
        authentication = YasoundApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        
    def override_urls(self):
        return [
            url(r"^radio/(?P<radio_id>\d+)/%s/$" % self._meta.resource_name, self.wrap_view('get_radio_user'), name="api_get_radio_user"),
        ]
        
    def get_radio_user(self, request, **kwargs):        
        self.method_check(request, self._meta.allowed_methods)
        self.is_authenticated(request)
        
        radio_id = kwargs.pop('radio_id')
        radio = get_object_or_404(Radio, id=radio_id)
        
        # create RadioUSer object if it does not exist
        radio_user, created = RadioUser.objects.get_or_create(radio=radio, user=request.user)
        
        resource = RadioUserResource() 
        return resource.get_detail(request, radio=radio, user=request.user)

   
class SongUserResource(ModelResource): 
#    song = fields.ForeignKey(SongInstanceResource, 'song', full=True)
    user = fields.ForeignKey(UserResource, 'user', full=True)   
    class Meta:
        queryset = SongUser.objects.all()
        resource_name = 'song_user'
        fields = ['song', 'user', 'mood']
        allowed_methods = ['get']
        include_resource_uri = False
        authentication = YasoundApiKeyAuthentication()
        authorization = ReadOnlyAuthorization()
        
    def override_urls(self):
        return [
            url(r"^song/(?P<song_id>\d+)/%s/$" % self._meta.resource_name, self.wrap_view('get_song_user'), name="api_get_song_user"),
        ]
        
    def get_song_user(self, request, **kwargs): 
        print 'get_song_user'       
        self.method_check(request, self._meta.allowed_methods)
        self.is_authenticated(request)
        
        song_id = kwargs.pop('song_id')
        song = get_object_or_404(SongInstance, id=song_id)
        
        # create SongUser object if it does not exist
        song_user, created = SongUser.objects.get_or_create(song=song, user=request.user)
        
        resource = SongUserResource() 
        return resource.get_detail(request, song=song, user=request.user)
    
    def dehydrate(self, bundle):
        song_user = bundle.obj
        song_desc = song_user.song.song_description
        bundle.data['song'] = song_desc
        return bundle



class RadioEnabledPlaylistResource(ModelResource):
    radio = fields.ForeignKey(RadioResource, 'radio')
    
    class Meta:
        queryset = Playlist.objects.filter(enabled=True).exclude(name=yabase_settings.YASOUND_FAVORITES_PLAYLIST_NAME)
        resource_name = 'enabled_playlist'
        fields = ['id', 'name']
        include_resource_uri = False
        authorization= ReadOnlyAuthorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = ['get']
        filtering = {
            'radio': 'exact',
            }

    def dispatch(self, request_type, request, **kwargs):
        radio = kwargs.pop('radio')
        kwargs['radio'] = get_object_or_404(Radio, id=radio)
        return super(RadioEnabledPlaylistResource, self).dispatch(request_type, request, **kwargs)
    
class RadioAllPlaylistResource(ModelResource):
    """
    return all playlists for a given radio
    """
    radio = fields.ForeignKey(RadioResource, 'radio')
    song_count = fields.IntegerField(attribute='song_count', default=0, readonly=True)
    matched_song_count = fields.IntegerField(attribute='matched_song_count', default=0, readonly=True)
    unmatched_song_count = fields.IntegerField(attribute='unmatched_song_count', default=0, readonly=True)
    class Meta:
        queryset = Playlist.objects.exclude(name=yabase_settings.YASOUND_FAVORITES_PLAYLIST_NAME)
        resource_name = 'all_playlist'
        fields = ['id', 
                  'name', 
                  'source', 
                  'enabled', 
                  'sync_date',]
        include_resource_uri = False
        authorization= ReadOnlyAuthorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = ['get']
        filtering = {
            'radio': 'exact',
            }

    def dispatch(self, request_type, request, **kwargs):
        radio = kwargs.pop('radio')
        kwargs['radio'] = get_object_or_404(Radio, id=radio)
        return super(RadioAllPlaylistResource, self).dispatch(request_type, request, **kwargs)
        
        
    
class MatchedSongAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        return True

    def apply_limits(self, request, object_list):
        return object_list.filter(playlist__radio__creator=request.user)
        
    
class MatchedSongResource(ModelResource):  
    class Meta:
        playlist = None
        queryset = SongInstance.objects.all()
        resource_name = 'matched_song'
        fields = ['id',
                  'last_play_time',
                  'frequency',
                  'enabled',
                  'likes'
                  ]
        include_resource_uri = False
        authorization= MatchedSongAuthorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = ['get']
        
    def dispatch(self, request_type, request, **kwargs):
        playlist_id = kwargs.pop('playlist')
        self.playlist = get_object_or_404(Playlist, id=playlist_id)
        return super(MatchedSongResource, self).dispatch(request_type, request, **kwargs)
    
    def get_object_list(self, request):
        song_instances = SongInstance.objects.select_related('metadata').filter(playlist=self.playlist, metadata__yasound_song_id__isnull=False)
        return song_instances
    
    def dehydrate(self, bundle):
        song_instance = bundle.obj
        
        bundle.data['name'] = song_instance.metadata.name
        bundle.data['artist'] = song_instance.metadata.artist_name
        bundle.data['album'] = song_instance.metadata.album_name

#        if yasound_song.album:
#            cover = yasound_song.album.cover_url
#        elif yasound_song.cover_filename:
#            cover = yasound_song.cover_url
#        else:
#            cover = None
        cover = None
        bundle.data['cover'] = cover
    
        return bundle
        
    
class EditSongResource(ModelResource):  
    class Meta:
        playlist = None
        queryset = SongInstance.objects.all()
        resource_name = 'edit_song'
        fields = ['id',
                  'frequency',
                  'enabled',
                  ]
        include_resource_uri = False
        authorization= Authorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = ['put', 'delete']
    
    
#YASOUND_SONG_ID_PARAM_NAME = 'yasound_song'
#class AddSongResource(ModelResource):  
#    class Meta:
#        queryset = SongInstance.objects.all()
#        resource_name = 'add_song'
#        fields = ['frequency',
#                  ]
#        include_resource_uri = False
#        authorization= Authorization()
#        authentication = YasoundApiKeyAuthentication()
#        allowed_methods = ['post']
#        
#    def obj_create(self, bundle, request=None, **kwargs):
#        yasound_song_id = kwargs.pop(YASOUND_SONG_ID_PARAM_NAME)
#        try:
#            yasound_song = YasoundSong.objects.get(id=yasound_song_id)
#        except YasoundSong.DoesNotExist:
#            return None
#        
#        playlists = Playlist.filter(radio__creator=request.user)
#        if playlists.count() == 0:
#            return None
#        playlist = playlists[0]
#
#        song_instance_resource = super(AddSongResource, self).obj_create(bundle, request, **kwargs)
#        song_instance = song_instance_resource.obj
#        song_instance.playlist = playlist
#        
#        song_instance.metadata.yasound_song = yasound_song
#        song_instance.save()
#        return song_instance_resource
#        
class SearchSongResource(ModelResource):  
    class Meta:
        playlist = None
        queryset = YasoundSong.objects.all()
        resource_name = 'search_song'
        fields = ['id', 
                  'name',
                  'artist_name',
                  'album_name',
                  ]
        include_resource_uri = False
        authorization= ReadOnlyAuthorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = ['get']
        
    
    def get_object_list(self, request):
        search = request.GET.get('search', None)
        offset = int(request.GET.get('song_offset', 0))
        count = int(request.GET.get('song_count', 50))
        yasound_songs = YasoundSong.objects.search(search, offset=offset, count=count)
        return yasound_songs
    
    def obj_get_list(self, request=None, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(request)
    
    def dehydrate(self, bundle):
        yasound_song = bundle.obj
        if yasound_song.album:
            cover = yasound_song.album.cover_url
        elif yasound_song.cover_filename:
            cover = yasound_song.cover_url
        else:
            cover = None
        bundle.data['cover'] = cover      
        return bundle
    
    
class LeaderBoardResource(ModelResource):
    class Meta:
        queryset = Radio.objects.ready_objects()
        resource_name = 'leaderboard'
        fields = ['id', 'name', 'leaderboard_favorites', 'leaderboard_rank']
        include_resource_uri = False
        authorization= ReadOnlyAuthorization()
        authentication = YasoundApiKeyAuthentication()
        allowed_methods = ['get']
        
    def get_object_list(self, request):
        self.request_user = request.user
        try:
            user_radio = Radio.objects.filter(creator=request.user)[0]
        except Radio.DoesNotExist:
            return None
        return user_radio.relative_leaderboard()
        
    def obj_get_list(self, request=None, **kwargs):
        # Filtering disabled for brevity...
        return self.get_object_list(request)
    
    def dehydrate(self, bundle):
        radio = bundle.obj
        mine = radio.creator == self.request_user
        bundle.data['mine'] = mine
        return bundle


