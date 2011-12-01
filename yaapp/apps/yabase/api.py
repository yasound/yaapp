from tastypie import fields
from tastypie.resources import ModelResource
from yabase.models import SongMetadata, SongInstance, UserProfile, Playlist, RadioEvent, Radio
from django.contrib.auth.models import User
from django.conf.urls.defaults import url
from tastypie.utils import trailing_slash

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
    class Meta:
        queryset = Playlist.objects.all()
        resource_name = 'playlist'
        fields = ['name', 'source', 'enabled', 'sync_date', 'CRC']
        include_resource_uri = False



class RadioResource(ModelResource):
    playlists = fields.ManyToManyField('yabase.api.PlaylistResource', 'playlists', full=True)
    #picture
    wall = fields.ToManyField('yabase.api.RadioEventResource', 'wall', full=False)
    next_songs = fields.ManyToManyField('yabase.api.RadioEventResource', 'next_songs', full=True)
    connected_users = fields.ManyToManyField('yabase.api.UserProfileResource', 'connected_users', full=True)
    users_with_this_radio_as_favorite = fields.ManyToManyField('yabase.api.UserProfileResource', 'users_with_this_radio_as_favorite', full=True)
    likes = fields.ManyToManyField('yabase.api.UserProfileResource', 'likes', full=True)
    dislikes = fields.ManyToManyField('yabase.api.UserProfileResource', 'dislikes', full=True)
    
    class Meta:
        queryset = Radio.objects.all()
        resource_name = 'radio'
        fields = ['name', 'playlists', 'picture', 'description', 'creation_date', 'wall', 'next_songs', 'url', 'connected_users', 'users_with_this_radio_as_favorite', 'audience_peak', 'likes', 'dislikes', 'overall_listening_time']
        include_resource_uri = False
    
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/wall%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_wall'), name="api_get_wall"),
        ]

    def get_wall(self, request, **kwargs):
        try:
            obj = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices("More than one resource is found at this URI.")
        
        wall_event_resource = RadioEventResource()
        return wall_event_resource.get_detail(request, wall_events=obj.pk) # to fix...







class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        fields = ['username', 'first_name', 'last_name']
        include_resource_uri = False

class UserProfileResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True)
    #picture
    radios = fields.ManyToManyField(RadioResource, 'radios', full=True)
    favorites = fields.ManyToManyField(RadioResource, 'favorites', full=True)
    likes = fields.ManyToManyField(RadioResource, 'likes', full=True)
    dislikes = fields.ManyToManyField(RadioResource, 'dislikes', full=True)
    class Meta:
        queryset = UserProfile.objects.all()
        resource_name = 'user'
        fields = ['user', 'join_date', 'last_login_time', 'url', 'twitter_account', 'facebook_account', 'picture', 'radios', 'bio_text', 'favorites', 'likes', ' dislikes', 'selection', 'last_selection_date']
        include_resource_uri = False


class RadioEventResource(ModelResource):
    song = fields.ForeignKey(SongInstanceResource, 'song', full=True, null=True)
    user = fields.ForeignKey(UserProfileResource, 'user', full=True, null=True)
    #picture
    class Meta:
        queryset = RadioEvent.objects.all()
        resource_name = 'radio_event'
        fields = ['type', 'start_date', 'end_date', 'song', 'old_id', 'user', 'text', 'animated_emoticon', 'picture']
        include_resource_uri = False
