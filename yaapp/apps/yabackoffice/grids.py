from account.models import UserProfile
from extjs import grids
from yabase.models import SongInstance, Radio
from yainvitation.models import Invitation
from yaref.models import YasoundSong

class SongInstanceGrid(grids.ModelGrid):
    model = SongInstance
    list_mapping=[
            'id',
            ]
    mapping = {
        'name' : 'metadata__name',
        'artist_name': 'metadata__artist_name',
        'album_name' : 'metadata__album_name'
    }
    
    
class RadioGrid(grids.ModelGrid):
    model = Radio
    list_mapping=[
            'id',
            'name',
            'creator',
            ]
    mapping = {
        'picture': 'picture_url',
        'creator_id': 'creator__id',
        'creator_profile': 'creator__userprofile',
        'creator_profile_id': 'creator__userprofile__id'
    }
    
class InvitationGrid(grids.ModelGrid):
    model = Invitation
    list_mapping=[
            'id',
            'fullname',
            'user',
            'email',
            'key',
            'sent'
            ]
    mapping = {
            'radio_name': 'radio__name'
    }
    
    
class YasoundSongGrid(grids.ModelGrid):
    model = YasoundSong
    list_mapping=[
            'id',
            'name',
            'artist_name',
            'album_name',
            ]
    mapping = {
    }
    
class UserProfileGrid(grids.ModelGrid):
    model = UserProfile
    list_mapping=[
            'id',
            'account_type',
            'facebook_uid',
            'last_authentication_date',
            ]
    mapping = {
            'name': 'fullname',
            'user_id': 'user__id',
            'is_superuser': 'user__is_superuser',
    }
