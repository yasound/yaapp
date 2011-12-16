from yabase.models import *
from django.contrib import admin

admin.site.register(SongMetadata)
admin.site.register(SongInstance)
admin.site.register(Playlist)
admin.site.register(Radio)
admin.site.register(WallEvent)
admin.site.register(NextSong)
admin.site.register(RadioUser)
admin.site.register(SongUser)

# yasound read only song db:
class YasoundSongAdmin(admin.ModelAdmin):
    list_display = ('name')


admin.site.register(YasoundSong)
admin.site.register(YasoundArtist)
admin.site.register(YasoundAlbum)
admin.site.register(YasoundGenre)
admin.site.register(YasoundSongGenre)

