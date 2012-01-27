from django.contrib import admin
from models import SongMetadata, SongInstance, Playlist, Radio, WallEvent, \
    NextSong, RadioUser, SongUser

class SongMetadataAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist_name', 'album_name' )
    search_fields = ( 'name', 'artist_name', 'album_name', )

class SongInstanceAdmin(admin.ModelAdmin):
    list_display = ('song', )
    #search_fields = ( 'metadata.name', 'metadata.artist_name', 'metadata.album_name', )
    
class WallEventAdmin(admin.ModelAdmin):
    list_display = ('radio', 'type', 'start_date', 'song', 'user', 'text')
    
    
admin.site.register(SongMetadata, SongMetadataAdmin)
admin.site.register(SongInstance, SongInstanceAdmin)
admin.site.register(Playlist)
admin.site.register(Radio)
admin.site.register(WallEvent, WallEventAdmin)
admin.site.register(NextSong)
admin.site.register(RadioUser)
admin.site.register(SongUser)
