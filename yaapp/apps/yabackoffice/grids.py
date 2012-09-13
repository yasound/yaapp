from account.models import UserProfile
from extjs import grids
from yabackoffice.models import BackofficeRadio
from yabase.models import SongInstance, WallEvent
from yainvitation.models import Invitation
from yaref.models import YasoundSong
from yapremium.models import Promocode
from yageoperm.models import Country


class SongInstanceGrid(grids.ModelGrid):
    model = SongInstance
    list_mapping = [
            'id',
            ]
    mapping = {
        'name': 'metadata__name',
        'artist_name': 'metadata__artist_name',
        'album_name': 'metadata__album_name',
        'yasound_song_id': 'metadata__yasound_song_id'
    }


class RadioGrid(grids.ModelGrid):
    model = BackofficeRadio
    list_mapping = [
            'id',
            'name',
            'created',
            'creator',
            'song_count',
            ]
    mapping = {
        'picture': 'picture_url',
        'creator_id': 'creator__id',
        'creator_profile': 'creator__userprofile',
        'creator_profile_id': 'creator__userprofile__id',
    }


class InvitationGrid(grids.ModelGrid):
    model = Invitation
    list_mapping = [
            'id',
            'fullname',
            'user',
            'email',
            'invitation_key',
            'radio',
            'subject',
            'message',
            'sent'
            ]
    mapping = {
            'radio_id': 'radio__id',
            'user_profile': 'user__userprofile',
    }


class YasoundSongGrid(grids.ModelGrid):
    model = YasoundSong
    list_mapping = [
            'id',
            'name',
            'artist_name',
            'album_name',
    ]


class UserProfileGrid(grids.ModelGrid):
    model = UserProfile
    list_mapping = [
            'id',
            'account_type',
            'facebook_uid',
            'last_authentication_date',
            ]
    mapping = {
            'name': 'fullname',
            'user_id': 'user__id',
            'is_superuser': 'user__is_superuser',
            'is_active': 'user__is_active',
            'date_joined': 'user__date_joined',
            'email': 'user__email',
    }


class WallEventGrid(grids.ModelGrid):
    model = WallEvent
    list_mapping = [
            'id',
            'type',
            'user_name',
            'text',
            ]
    exclude = ['picture', 'user_picture']
    mapping = {}


class PromocodeGrid(grids.ModelGrid):
    model = Promocode
    list_mapping = [
        'id',
        'service',
        'code',
        'created',
        'enabled',
        'duration'
    ]
    mapping = {
        'service_id': 'service__id',
    }


class CountryGrid(grids.ModelGrid):
    model = Country
