from models import SongMetadata, SongInstance, Playlist, Radio, \
    WallEvent, NextSong, RadioUser, SongUser, YasoundSong, YasoundArtist, \
    YasoundAlbum, YasoundGenre, YasoundSongGenre, YasoundDoubleMetaphone
from django.contrib import admin

class SongMetadataAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist_name', 'album_name' )
    search_fields = ( 'name', 'artist_name', 'album_name', )

class SongInstanceAdmin(admin.ModelAdmin):
    list_display = ('song', )
    #search_fields = ( 'metadata.name', 'metadata.artist_name', 'metadata.album_name', )


admin.site.register(SongMetadata, SongMetadataAdmin)
admin.site.register(SongInstance, SongInstanceAdmin)
admin.site.register(Playlist)
admin.site.register(Radio)
admin.site.register(WallEvent)
admin.site.register(NextSong)
admin.site.register(RadioUser)
admin.site.register(SongUser)

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

