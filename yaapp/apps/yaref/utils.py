import subprocess as sub
import os
from django.conf import settings
import random
import requests
import pyquery

import musicbrainz2.webservice as ws
from pyquery import PyQuery as pq

import logging
logger = logging.getLogger("yaapp.yaref")


def convert_filename_to_filepath(filename):
    """
    123456789.jpg --> 123/456/789.jpg
    """
    if len(filename) != len('123456789.jpg'):
        return None
    part1 = filename[:3]
    part2 = filename[3:6]
    part3 = filename[6:9]
    extension = filename[-3:]
    return '%s/%s/%s.%s' % (part1, part2, part3, extension)


def convert_to_mp3(ffmpeg_bin, ffmpeg_options, source, destination):
    args = [ffmpeg_bin,
            '-i',
            source]
    args.extend(ffmpeg_options.split(" "))
    args.append(destination)
    p = sub.Popen(args, stdout=sub.PIPE, stderr=sub.PIPE)
    output, errors = p.communicate()
    if len(errors) == 0:
        return False
    return True


def generate_filename_and_path_for_song_cover(extension='.jpg'):
    path_exists = True
    filename = None
    while path_exists:
        filename = ''.join(random.choice("01234567890abcdef") for _i in xrange(9)) + extension
        path = os.path.join(settings.SONG_COVERS_ROOT, convert_filename_to_filepath(filename))
        path_exists = os.path.exists(path)
    return filename, path

def generate_filename_and_path_for_album_cover(extension='.jpg'):
    path_exists = True
    filename = None
    while path_exists:
        filename = ''.join(random.choice("01234567890abcdef") for _i in xrange(9)) + extension
        path = os.path.join(settings.ALBUM_COVERS_ROOT, convert_filename_to_filepath(filename))
        path_exists = os.path.exists(path)
    return filename, path


def find_cover(mbid):
    q = ws.Query()
    try:
        inc = ws.ReleaseIncludes(artist=True, releaseEvents=True, labels=True,
                discs=True, tracks=True, releaseGroup=True, releaseRelations=True,
                trackRelations=True, urlRelations=True)
        release = q.getReleaseById(mbid, inc)
    except ws.WebServiceError, e:
        logger.error(e)
        return None, None

    relation = None
    relations = release.getRelations()
    for rel in relations:
        if rel.getType() == u'http://musicbrainz.org/ns/rel-1.0#AmazonAsin':
            relation = rel
            break

    if relation is None:
        return None, None

    url = relation.targetId

    logger.debug('url of relation: %s' % (url))
    amazon_page = requests.get(url)
    if amazon_page.status_code != 200:
        return None, None

    content = amazon_page.content
    d = pq(content)
    image = d('#prodImage')
    url = image.attr('src')
    if url is None:
        image = d('#main-image')
        url = image.attr('src')
    if url is None:
        return None, None

    logger.debug('--> downloading image: %s' % (url))
    res = requests.get(url)
    if res.status_code != 200:
        return None, None
    content = res.content
    content_type = res.headers.get('content-type')
    extension = '.jpg'
    if content_type == 'image/jpeg':
        extension = '.jpg'
    elif content_type == 'image/png':
        extension = '.png'
    return content, extension
