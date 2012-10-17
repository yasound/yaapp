"""
Models for radioways.
All models have a "radioways_id" which is the primary key in the radioways database.
"""

from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import settings as radioways_settings

from yabase.models import Radio as YasoundRadio
from yageoperm.models import Country as YasoundCountry
from yabase import settings as yabase_settings

from yametadata.radioways import find_metadata
from sorl.thumbnail import get_thumbnail
import logging
logger = logging.getLogger("yaapp.radioways")


class Continent(models.Model):
    """A continent.
    Contains a code (aka sigle) and fr, uk, es & de names.
    """
    radioways_id = models.IntegerField(_('radioways id'), unique=True)
    sigle = models.CharField(_('sigle'), max_length=4, blank=True)
    name_fr = models.CharField(_('name (fr)'), max_length=100, blank=True)
    name_uk = models.CharField(_('name (uk)'), max_length=100, blank=True)
    name_es = models.CharField(_('name (es)'), max_length=100, blank=True)
    name_de = models.CharField(_('name (de)'), max_length=100, blank=True)

    def __unicode__(self):
        return self.name_fr


class Country(models.Model):
    """A country, linked with a continent.
    Contains a code (aka sigle) and fr, uk, es & de names.
    """
    radioways_id = models.IntegerField(_('radioways id'), unique=True)
    continent = models.ForeignKey(Continent, verbose_name=_('continent'))
    sigle = models.CharField(_('sigle'), max_length=4, blank=True)
    name_fr = models.CharField(_('name (fr)'), max_length=100, blank=True)
    name_uk = models.CharField(_('name (uk)'), max_length=100, blank=True)
    name_es = models.CharField(_('name (es)'), max_length=100, blank=True)
    name_de = models.CharField(_('name (de)'), max_length=100, blank=True)

    def __unicode__(self):
        return self.name_fr


class Genre(models.Model):
    """Genre.
    A genre has a type and name. Genre is translated as tags in yasound radio
    """
    radioways_id = models.IntegerField(_('radioways id'), unique=True)
    gtype = models.IntegerField(_('type'), choices=radioways_settings.GENRE_TYPE_CHOICES, default=radioways_settings.GENRE_TYPE_MUSICAL)
    name_fr = models.CharField(_('name (fr)'), max_length=100, blank=True)
    name_uk = models.CharField(_('name (uk)'), max_length=100, blank=True)
    name_es = models.CharField(_('name (es)'), max_length=100, blank=True)
    name_de = models.CharField(_('name (de)'), max_length=100, blank=True)

    def __unicode__(self):
        return self.name_fr


class Radio(models.Model):
    """Radioways radio
    A radio, linked with an optional foreign key
    """
    radioways_id = models.IntegerField(_('radioways id'), unique=True)
    yasound_radio = models.OneToOneField('yabase.Radio',
                                         verbose_name=_('yasound radio'),
        blank=True,
        null=True,
        related_name='radioways_radio',
        on_delete=models.SET_NULL)
    genres = models.ManyToManyField(Genre, verbose_name=_('genres'), blank=True, null=True)
    country = models.ForeignKey(Country, verbose_name=_('country'))
    name = models.CharField(_('name'), max_length=255, blank=True)
    rtype = models.IntegerField(_('type'), choices=radioways_settings.RADIOWAYS_TYPE_CHOICES)
    city = models.CharField(_('city'), max_length=255, blank=True)
    website = models.URLField(_('website'), max_length=255, blank=True)
    rate_mm = models.IntegerField(_('rateMM'), default=0)
    logo = models.IntegerField(_('logo id'), default=0)
    logo_small = models.IntegerField(_('logo id (small version)'), default=0)
    stream_url = models.URLField(_('stream url'), max_length=255, blank=True)
    metadata_id = models.IntegerField(_('metadata id'), default=0)
    bitrate = models.SmallIntegerField(_('bitrate'), default=0)
    stream_codec = models.IntegerField(_('codec'), choices=radioways_settings.CODEC_CHOICES, default=radioways_settings.CODEC_MP3)
    stream_response_time = models.IntegerField(_('stream response time'), null=True, blank=True)

    def link_to_yasound(self):
        """Create or update the associated yasound radio.

        """
        country = self.country
        sigle = country.sigle
        city = self.city
        stream_url = self.stream_url
        genres = self.genres.all()
        tags = ''
        for genre in genres:
            tag = '%s, %s, %s, %s' % (genre.name_fr, genre.name_uk, genre.name_es, genre.name_de)
            tags = tags + ', ' + tag
        yasound_username = 'yasound_%s' % (sigle)

        user, _created = User.objects.get_or_create(username=yasound_username)
        if user.get_profile().name == '':
            profile = user.get_profile()
            profile.name = 'Yasound %s' % (sigle)
            profile.save()
        yasound_country, _created = YasoundCountry.objects.get_or_create(code=sigle, defaults={'name': unicode(self.country)})

        logger.info('creating %s' % self.name)
        yasound_radio = YasoundRadio.objects.create(name=self.name,
            origin=yabase_settings.RADIO_ORIGIN_RADIOWAYS,
            creator=user,
            country=yasound_country,
            city=city,
            ready=True,
            url=stream_url)
        yasound_radio.set_tags(tags)

        self.yasound_radio = yasound_radio
        self.save()

    @property
    def current_song(self):
        """Return the current song.
        the returned data is a dict::

            dict = {
                'id': None,
                'name': None,
                'artist': None,
                'album': None,
                'cover': None,
                'large_cover': None
            }

        """

        song_dict = {
            'id': None,
            'name': None,
            'artist': None,
            'album': None,
            'cover': settings.DEFAULT_TRACK_IMAGE,
            'large_cover': settings.DEFAULT_TRACK_IMAGE
        }
        res = find_metadata(self.metadata_id)
        if not res:
            return song_dict

        metadata = res.get('metadata', {})
        song_dict['name'] = metadata.get('title')
        song_dict['artist'] = metadata.get('artist')
        return song_dict

    def get_cover_url(self, size='64x64'):
        """return cover url, max size is 64x64 (constrained)
        """
        size_n = size.split('x')
        if int(size_n[0]) > 64:
            size = '64x64'

        short_url = '%s%s.png' % (settings.RADIOWAYS_COVER_SHORT_URL, self.radioways_id)
        try:
            return get_thumbnail(short_url, size, crop='center').url
        except:
            return get_thumbnail(settings.DEFAULT_IMAGE_PATH, size, crop='center').url

    @property
    def cover_url(self):
        """return standard cover url (64x64)
        """

        return self.get_cover_url(size='64x64')

    def __unicode__(self):
        return self.name
