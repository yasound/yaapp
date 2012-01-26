from django.contrib import admin
from models import YasoundSong, YasoundArtist, YasoundAlbum, YasoundGenre, \
    YasoundSongGenre, YasoundDoubleMetaphone

# yasound read only song db:
class YasoundSongAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist_name', 'album_name' )
    search_fields = ( 'name', 'artist_name', 'album_name', )


admin.site.register(YasoundSong, YasoundSongAdmin)
admin.site.register(YasoundArtist)
admin.site.register(YasoundAlbum)
admin.site.register(YasoundGenre)
admin.site.register(YasoundSongGenre)
admin.site.register(YasoundDoubleMetaphone)

