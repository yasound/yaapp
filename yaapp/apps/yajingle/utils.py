import random
import os
from yaref.utils import convert_filename_to_filepath
from django.conf import settings


def generate_filename_and_path_for_jingle():
    """
    return filename, fullpath
    """
    path_exists = True
    filename = None
    while path_exists:
        filename = ''.join(random.choice("01234567890abcdef") for _i in xrange(9)) + '.mp3'
        path = os.path.join(settings.SONGS_ROOT, convert_filename_to_filepath(filename))
        path_exists = os.path.exists(path)
    return filename, path
