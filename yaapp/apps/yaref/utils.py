import subprocess as sub
import os
from django.conf import settings
import random
import requests


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


def generate_filename_and_path_for_song_cover(self, extension='.jpg'):
    path_exists = True
    filename = None
    while path_exists:
        filename = ''.join(random.choice("01234567890abcdef") for _i in xrange(9)) + extension
        path = os.path.join(settings.SONG_COVERS_ROOT, convert_filename_to_filepath(filename))
        path_exists = os.path.exists(path)
    return filename, path


def find_cover(mbid):
    url = 'http://coverartarchive.org/release/%s/front' % (mbid)
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
