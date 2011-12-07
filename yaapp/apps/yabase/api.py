from tastypie import fields
from tastypie.resources import ModelResource
from yabase.models import SongMetadata, SongInstance, Playlist, Radio, WallEvent, NextSong
from django.contrib.auth.models import User
from django.conf.urls.defaults import url
from django.shortcuts import get_object_or_404
from tastypie.utils import trailing_slash
import datetime

class SongMetadataResource(ModelResource):
    class Meta:
        queryset = SongMetadata.objects.all()
        resource_name = 'metadata'
        fields = ['name', 'artist_name', 'album_name', 'track_index', 'track_count', 'disc_index', 'disc_count', 'bpm', 'date', 'score', 'duration', 'genre', 'picture']
        include_resource_uri = False

class SongInstanceResource(ModelResource):
    metadata = fields.OneToOneField(SongMetadataResource, 'metadata', full=True)
    class Meta:
        queryset = SongInstance.objects.all()
        resource_name = 'song'
        fields = ['song', 'play_count', 'last_play_time', 'yasound_score', 'metadata']
        include_resource_uri = False

class PlaylistResource(ModelResource):
    songs = fields.ManyToManyField(SongInstanceResource, 'songs')
    class Meta:
        queryset = Playlist.objects.all()
        resource_name = 'playlist'
        fields = ['name', 'source', 'enabled', 'sync_date', 'CRC', 'songs']
        include_resource_uri = False



class RadioResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=True)
    
    users = fields.ManyToManyField('yabase.api.UserResource', 'users')
    next_songs = fields.ManyToManyField(SongInstanceResource, 'next_songs')
    
    class Meta:
        queryset = Radio.objects.all()
        resource_name = 'radio'
        fields = ['creator', 'created', 'updated', 'playlists', 'name', 'picture', 'url' 'description', 'audience_peak', 'overall_listening_time', 'users', 'next_songs']
        include_resource_uri = False;

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name']
        include_resource_uri = False


class WallEventResource(ModelResource):
    radio = fields.ForeignKey(RadioResource, 'radio')
    song = fields.ForeignKey(SongInstanceResource, 'song', full=True, null=True)
    user = fields.ForeignKey(UserResource, 'user', full=True, null=True)
    class Meta:
        queryset = WallEvent.objects.all()
        resource_name = 'wall'
        fields = ['type', 'start_date', 'end_date', 'song', 'old_id', 'user', 'text', 'animated_emoticon', 'picture', 'radio']
        include_resource_uri = False
        filtering = {
            'radio': 'exact',
        }

    def dispatch(self, request_type, request, **kwargs):
        radio = kwargs.pop('radio')
        kwargs['radio'] = get_object_or_404(Radio, id=radio)
        return super(WallEventResource, self).dispatch(request_type, request, **kwargs)


class NextSongsResource(ModelResource):
    song = fields.ForeignKey(SongInstanceResource, 'song')
    radio = fields.ForeignKey(RadioResource, 'radio')
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
        queryset = User.objects.filter(radiouser__mood='L')
        resource_name = 'likes'
        fields = ['username']
        include_resource_uri = False
    
    def dispatch(self, request_type, request, **kwargs):
        radioID = kwargs.pop('radio')
        self.radio = get_object_or_404(Radio, id=radioID)
#        kwargs['radiouser_set__radio'] = get_object_or_404(Radio, id=radioID)
        return super(RadioLikerResource, self).dispatch(request_type, request, **kwargs)
    
    def get_object_list(self, request):
        return super(RadioLikerResource, self).get_object_list(request).filter(radiouser__radio=self.radio)

