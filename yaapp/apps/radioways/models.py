from django.db import models
from django.utils.translation import ugettext_lazy as _
import settings as radioways_settings

import logging
logger = logging.getLogger("yaapp.radioways")


class Continent(models.Model):
    radioways_id = models.IntegerField(_('radioways id'), unique=True)
    sigle = models.CharField(_('sigle'), max_length=4, blank=True)
    name_fr = models.CharField(_('name (fr)'), max_length=100, blank=True)
    name_uk = models.CharField(_('name (uk)'), max_length=100, blank=True)
    name_es = models.CharField(_('name (es)'), max_length=100, blank=True)
    name_de = models.CharField(_('name (de)'), max_length=100, blank=True)

    def __unicode__(self):
        return self.name_fr


class Country(models.Model):
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
    radioways_id = models.IntegerField(_('radioways id'), unique=True)
    gtype = models.IntegerField(_('type'), choices=radioways_settings.GENRE_TYPE_CHOICES, default=radioways_settings.GENRE_TYPE_MUSICAL)
    name_fr = models.CharField(_('name (fr)'), max_length=100, blank=True)
    name_uk = models.CharField(_('name (uk)'), max_length=100, blank=True)
    name_es = models.CharField(_('name (es)'), max_length=100, blank=True)
    name_de = models.CharField(_('name (de)'), max_length=100, blank=True)

    def __unicode__(self):
        return self.name_fr


class Radio(models.Model):
    radioways_id = models.IntegerField(_('radioways id'), unique=True)
    yasound_radio = models.OneToOneField('yabase.Radio', verbose_name=_('yasound radio'), blank=True, null=True)
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

    def __unicode__(self):
        return self.name
