from django.contrib.auth.models import User
from celery.task import task
from account.models import UserProfile
from django.conf import settings
from yaref.utils import convert_to_mp3, convert_filename_to_filepath2
import os
import logging
logger = logging.getLogger("yaapp.yajingle")
import shutil
import random
import errno
from yabase.models import Radio
from models import JingleManager


def _generate_filename_and_path_for_jingle():
    path_exists = True
    filename = None
    while path_exists:
        filename = ''.join(random.choice("01234567890abcdef") for _i in xrange(9)) + '.mp3'
        path = os.path.join(settings.JINGLES_ROOT, convert_filename_to_filepath2(filename))
        path_exists = os.path.exists(path)
    return filename, path


@task
def import_jingle(filename, name, radio_uuid, creator_id):
    radio = Radio.objects.get(uuid=radio_uuid)
    creator = User.objects.get(id=creator_id)
    directory = os.path.dirname(filename)
    converted = u'%s/d.mp3' % (directory)
    res = convert_to_mp3(settings.FFMPEG_BIN, settings.FFMPEG_CONVERT_HIGH_QUALITY_OPTIONS, filename, converted)
    if not res:
        logger.error('cannot convert %s to %s' % (filename, converted))
        return

    jingle_filename, jingle_path = _generate_filename_and_path_for_jingle()
    try:
        os.makedirs(os.path.dirname(jingle_path))
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise

    shutil.copy(converted, jingle_path)

    m = JingleManager()
    m.create_jingle(name=name, radio=radio, creator=creator, filename=jingle_filename)
