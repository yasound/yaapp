from extjs import grids
from yabase.models import SongInstance

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
    