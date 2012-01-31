from django.contrib import admin
from models import YasoundSong, YasoundArtist, YasoundAlbum, YasoundGenre, \
    YasoundSongGenre

# yasound read only song db:
class YasoundSongAdmin(admin.ModelAdmin):
    list_display = ('name', 'echonest_id', 'lastfm_id', 'duration', 'filename', 'artist_name', 'album_name' )
    search_fields = ( 'name_simplified', 'artist_name_simplified', 'album_name_simplified', )
    


admin.site.register(YasoundSong, YasoundSongAdmin)
admin.site.register(YasoundArtist)
admin.site.register(YasoundAlbum)
admin.site.register(YasoundGenre)
admin.site.register(YasoundSongGenre)

