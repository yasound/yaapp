from django.contrib import admin
from models import YasoundSong, YasoundArtist, YasoundAlbum, YasoundGenre, \
    YasoundSongGenre

# yasound read only song db:
class YasoundSongAdmin(admin.ModelAdmin):
    list_display = ('name', 'echonest_id', 'lastfm_id', 'duration', 'filename', 'artist_name', 'album_name' )
    raw_id_fields = ('artist', 'album',)
    search_fields = ( 'id', 'name_simplified', 'artist_name_simplified', 'album_name_simplified', )
admin.site.register(YasoundSong, YasoundSongAdmin)


class YasoundArtistAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'name_simplified', 'lastfm_id', 'echonest_id', 'musicbrainz_id', )
    search_fields = ( 'id', 'name_simplified', )
admin.site.register(YasoundArtist, YasoundArtistAdmin)

class YasoundAlbumAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'name_simplified', 'lastfm_id', 'musicbrainz_id', )
    search_fields = ( 'id', 'name_simplified', )
admin.site.register(YasoundAlbum, YasoundAlbumAdmin)

admin.site.register(YasoundGenre)


class YasoundSongGenreAdmin(admin.ModelAdmin):
    list_display = ('song', 'genre', )
    raw_id_fields = ('song',)
    list_filter = ('genre', )
    search_fields = ( 'song__name_simplified', 'name_canonical', )
admin.site.register(YasoundSongGenre, YasoundSongGenreAdmin)

