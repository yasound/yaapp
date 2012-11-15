from django.contrib import admin
from models import SongMetadata, SongInstance, Playlist, Radio, WallEvent, \
    NextSong, RadioUser, SongUser, FeaturedContent, FeaturedRadio

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'source', 'radio', 'enabled', 'sync_date', 'CRC' )
    search_fields = ( 'name', 'source', )
    raw_id_fields = ('radio',)
admin.site.register(Playlist, PlaylistAdmin)


class RadioAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'creator', 'url', 'uuid', 'ready', 'deleted', 'origin', 'blacklisted')
    list_filter = ('deleted', 'origin', 'blacklisted')
    search_fields = ['name',]
    raw_id_fields = ('current_song', 'creator')
    exclude = ('next_songs', )
admin.site.register(Radio, RadioAdmin)


class SongMetadataAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist_name', 'album_name', 'yasound_song_id', 'hash_name')
    search_fields = ( 'name', 'artist_name', 'album_name', )
    actions = ['generate_hash_name',]
    def generate_hash_name(self, request, qs):
        for metadata in qs.all():
            metadata.calculate_hash_name(commit=True)
    generate_hash_name.short_description = "Generate hash name"

admin.site.register(SongMetadata, SongMetadataAdmin)

class SongInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'playlist', 'metadata_name', 'metadata_album', 'metadata_artist', 'yasound_song_id', 'need_sync')
    search_fields = ('song', 'metadata__yasound_song_id', 'metadata__name', 'metadata__album_name', 'metadata__artist_name')
    raw_id_fields = ('metadata', 'playlist')

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
    list_filter = ('type', 'radio',)
    search_fields = ['radio__name']
admin.site.register(WallEvent, WallEventAdmin)

class NextSongAdmin(admin.ModelAdmin):
    raw_id_fields = ('radio', 'song')
admin.site.register(NextSong, NextSongAdmin)

class FeaturedRadioInline(admin.TabularInline):
    raw_id_fields = ('radio',)
    model = FeaturedRadio
    extra = 1

class FeaturedContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'activated', 'ftype')
    search_fields = ['name']
    list_filter = ('activated', 'ftype')
    list_editable = ('activated', 'ftype')
    inlines = [FeaturedRadioInline]
admin.site.register(FeaturedContent, FeaturedContentAdmin)


# basic admin
class RadioUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'radio', 'user', 'favorite')
    raw_id_fields = ('radio', 'user')
admin.site.register(RadioUser, RadioUserAdmin)


class SongUserAdmin(admin.ModelAdmin):
    raw_id_fields = ('song', 'user')
admin.site.register(SongUser, SongUserAdmin)
