from extjs import grids
from yabase.models import SongInstance, Radio

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
            'creator'
            ]
    mapping = {
            'picture': 'picture_url'
    }