from django.contrib import admin
from models import SongMetadata, SongInstance, Playlist, Radio, WallEvent, \
    NextSong, RadioUser, SongUser, FeaturedContent, FeaturedRadio

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'source', 'radio', 'enabled', 'sync_date', 'CRC' )
    search_fields = ( 'name', 'source', )
    list_filter = ('radio',)
admin.site.register(Playlist, PlaylistAdmin)

    
class RadioAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'creator', 'url', 'uuid', 'ready')
    search_fields = ['name']
    raw_id_fields = ('current_song',)
    exclude = ('next_songs', )
    list_filter = ('creator', 'ready')
admin.site.register(Radio, RadioAdmin)
    

class SongMetadataAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist_name', 'album_name', 'yasound_song_id', )
    search_fields = ( 'name', 'artist_name', 'album_name', )
admin.site.register(SongMetadata, SongMetadataAdmin)

class SongInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'playlist', 'metadata_name', 'metadata_album', 'metadata_artist', 'yasound_song_id', 'need_sync')
    list_filter = ('playlist', 'need_sync')
    list_editable = ('playlist',)
    search_fields = ('song', 'metadata__yasound_song_id', 'metadata__name', 'metadata__album_name', 'metadata__artist_name')
    
    def metadata_name(self, obj):
        return obj.metadata.name
    metadata_name.short_description = 'Song'    
    def metadata_album(self, obj):
        return obj.metadata.album_name
    metadata_album.short_description = 'Album'    
    def metadata_artist(self, obj):
        return obj.metadata.artist_name
    metadata_artist.short_description = 'Artist'  
    def yasound_song_id(self, obj):
        return obj.metadata.yasound_song_id
    metadata_artist.short_description = 'Yasound Song Id'    
admin.site.register(SongInstance, SongInstanceAdmin)
    
class WallEventAdmin(admin.ModelAdmin):
    list_display = ('radio', 'type', 'start_date', 'song', 'user', 'text')
    raw_id_fields = ('radio', 'user', 'song')

admin.site.register(WallEvent, WallEventAdmin)

class NextSongAdmin(admin.ModelAdmin):
    list_filter = ('radio',)
admin.site.register(NextSong, NextSongAdmin)
    
class FeaturedRadioInline(admin.TabularInline):
    model = FeaturedRadio
    extra = 1    
    
class FeaturedContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'activated')
    search_fields = ['name']
    list_filter = ('activated',)
    list_editable = ('activated',)
    inlines = [FeaturedRadioInline]    
admin.site.register(FeaturedContent, FeaturedContentAdmin)


# basic admin     
admin.site.register(RadioUser)
admin.site.register(SongUser)
