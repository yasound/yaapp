from django.utils.translation import ugettext_lazy as _

CODEC_MP3 = 1
CODEC_MP4 = 2
CODEC_WMP = 3
CODEC_CHOICES = (
    (CODEC_MP3, _('mp3')),
    (CODEC_MP4, _('mp4')),
    (CODEC_WMP, _('wmp')),
)

RADIOWAYS_TYPE_RADIOFM = 1
RADIOWAYS_TYPE_WEBRADIO = 2
RADIOWAYS_TYPE_TV = 3
RADIOWAYS_TYPE_CHOICES = (
    (RADIOWAYS_TYPE_RADIOFM, _('radio fm')),
    (RADIOWAYS_TYPE_WEBRADIO, _('webradio')),
    (RADIOWAYS_TYPE_TV, _('tv')),
)


GENRE_TYPE_MUSICAL = 1
GENRE_TYPE_THEMATIC = 2
GENRE_TYPE_WORLD_MUSIC = 3
GENRE_TYPE_TV_MUSIC = 4
GENRE_TYPE_CHOICES = (
    (GENRE_TYPE_MUSICAL, _('musical')),
    (GENRE_TYPE_THEMATIC, _('thematic')),
    (GENRE_TYPE_WORLD_MUSIC, _('world music')),
    (GENRE_TYPE_TV_MUSIC, _('tv music')),
)
