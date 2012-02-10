from django.contrib import admin
from models import SongMetadata, SongInstance, Playlist, Radio, WallEvent, \
    NextSong, RadioUser, SongUser

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'source', 'radio', 'enabled', 'sync_date', 'CRC' )
    search_fields = ( 'name', 'source', )
    list_filter = ('radio',)
admin.site.register(Playlist, PlaylistAdmin)

    
class RadioAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'creator', 'url', 'uuid', 'ready')
    search_fields = ( 'name', )
    list_filter = ('creator', 'ready')
admin.site.register(Radio, RadioAdmin)
    

class SongMetadataAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist_name', 'album_name' )
    search_fields = ( 'name', 'artist_name', 'album_name', )

class SongInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'song', 'playlist', 'metadata_name', 'metadata_album', 'metadata_artist', 'need_sync')
    list_filter = ('playlist', 'need_sync')
    search_fields = ('song', 'metadata__name', 'metadata__album_name', 'metadata__artist_name')
    
    def metadata_name(self, obj):
        return obj.metadata.name
    metadata_name.short_description = 'Song'    
    def metadata_album(self, obj):
        return obj.metadata.album_name
    metadata_album.short_description = 'Album'    
    def metadata_artist(self, obj):
        return obj.metadata.artist_name
    metadata_artist.short_description = 'Artist'    
    
class WallEventAdmin(admin.ModelAdmin):
    list_display = ('radio', 'type', 'start_date', 'song', 'user', 'text')
    
    
admin.site.register(SongMetadata, SongMetadataAdmin)
admin.site.register(SongInstance, SongInstanceAdmin)
admin.site.register(WallEvent, WallEventAdmin)
admin.site.register(NextSong)
admin.site.register(RadioUser)
admin.site.register(SongUser)
