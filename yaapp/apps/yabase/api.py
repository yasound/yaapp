from tastypie import fields
from tastypie.resources import ModelResource
from yabase.models import SongMetadata, SongInstance, Playlist, Radio, WallEvent, NextSong, RadioUser
from django.contrib.auth.models import User
from django.conf.urls.defaults import url
from django.shortcuts import get_object_or_404
from tastypie.utils import trailing_slash
import datetime
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization


class SongMetadataResource(ModelResource):
    class Meta:
        queryset = SongMetadata.objects.all()
        resource_name = 'metadata'
        fields = ['name', 'artist_name', 'album_name', 'track_index', 'track_count', 'disc_index', 'disc_count', 'bpm', 'date', 'score', 'duration', 'genre', 'picture']
        include_resource_uri = False
        authorization= Authorization()
        authentication = Authentication()

class SongInstanceResource(ModelResource):
    metadata = fields.OneToOneField(SongMetadataResource, 'metadata', full=True)
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
    creator = fields.OneToOneField('yabase.api.UserResource', 'creator', full=False)
    url = fields.CharField('url')
    description = fields.CharField('description')
    
#    users = fields.ManyToManyField('yabase.api.UserResource', 'users')
#    next_songs = fields.ManyToManyField(SongInstanceResource, 'next_songs')
    
    # likers ?
    
    class Meta:
        queryset = Radio.objects.all()
        resource_name = 'radio'
        fields = ['id', 'creator', 'playlists', 'name', 'picture', 'url' 'description', 'genre', 'theme']
        include_resource_uri = False;


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['id', 'username', 'first_name', 'last_name']
        include_resource_uri = False

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
        return super(RadioLikerResource, self).get_object_list(request).filter(radiouser__radio=self.radio, radiouser__mood='L')


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
        queryset = WallEvent.objects.filter(type='S').order_by('-start_date')
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

   



