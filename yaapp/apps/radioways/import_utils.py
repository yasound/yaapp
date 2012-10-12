from models import Continent, Country, Genre, Radio
import settings as radioways_settings

import logging
logger = logging.getLogger("yaapp.radioways")

def _convert_to_utf8(str):
    try:
        encoded_str = str.decode("iso-8859-1").encode("UTF-8")
        return encoded_str
    except:
        return str


def import_continent(file):
    f = open(file)
    for i, line in enumerate(f):
        line = _convert_to_utf8(line.strip())
        if i == 0:
            continue

        content = line.split('\t')
        (radioways_id, sigle, fr, uk, es, de) = content

        continent, _created = Continent.objects.get_or_create(radioways_id=radioways_id)
        continent.sigle = sigle
        continent.radioways_id = radioways_id
        continent.name_fr = fr
        continent.name_uk = uk
        continent.name_es = es
        continent.name_de = de
        continent.save()


def import_country(file):
    f = open(file)
    for i, line in enumerate(f):
        line = _convert_to_utf8(line.strip())
        if i == 0:
            continue

        content = line.split('\t')
        (radioways_id, continent_id, sigle, fr, uk, es, de) = content
        continent = Continent.objects.get(radioways_id=continent_id)
        country, _created = Country.objects.get_or_create(radioways_id=radioways_id, defaults={'continent': continent})
        country.sigle = sigle
        country.radioways_id = radioways_id
        country.name_fr = fr
        country.name_uk = uk
        country.name_es = es
        country.name_de = de
        country.save()


def import_genre(file):
    f = open(file)
    for i, line in enumerate(f):
        line = _convert_to_utf8(line.strip())
        if i == 0:
            continue

        content = line.split('\t')
        (radioways_id, gtype, fr, uk, es, de) = content
        genre, _created = Genre.objects.get_or_create(radioways_id=radioways_id)
        genre.radioways_id = radioways_id
        genre.gtype = gtype
        genre.name_fr = fr
        genre.name_uk = uk
        genre.name_es = es
        genre.name_de = de
        genre.save()


def import_radio(file):
    f = open(file)
    for i, line in enumerate(f):
        line = _convert_to_utf8(line.strip())
        if i == 0:
            continue

        content = line.split('\t')
        if len(content) < 13:
            for j in range(len(content), 13):
                content.append('')

        (radioways_id,
            country_id,
            name,
            rtype,
            city,
            website,
            rate_mm,
            logo_id,
            stream_url,
            metadata_id,
            bitrate,
            stream_codec,
            stream_response_time) = content

        country = Country.objects.get(radioways_id=country_id)
        radio, _created = Radio.objects.get_or_create(radioways_id=radioways_id, defaults={'country': country, 'rtype': rtype})
        radio.name = name
        radio.city = city
        radio.website = website
        radio.rate_mm = rate_mm
        radio.logo_id = logo_id
        radio.stream_url = stream_url
        radio.metatad_id = metadata_id
        radio.bitrate = bitrate
        radio.stream_codec = stream_codec
        radio.stream_response_time = stream_response_time if stream_response_time != '' else None
        radio.save()


def import_radio_genre(file):
    f = open(file)
    for i, line in enumerate(f):
        line = _convert_to_utf8(line.strip())
        if i == 0:
            continue

        content = line.split('\t')
        (radio_id, genre_id) = content

        radio = Radio.objects.get(radioways_id=radio_id)
        genre = Genre.objects.get(radioways_id=genre_id)
        radio.genres.add(genre)

def link_to_yasound():
    qs = Radio.objects.filter(yasound_radio__isnull=True, stream_codec=radioways_settings.CODEC_MP3)
    logger.info('found %d radios to activate' % (qs.count()))
    for radio in qs:
        radio.link_to_yasound()
