from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
import datetime
from bson.objectid import ObjectId
from yaref.utils import convert_filename_to_filepath
import os
from django.utils.translation import ugettext_lazy as _
from yabase.models import Playlist
from yascheduler.task import async_transient_radio_event
from yascheduler.models import TransientRadioHistoryManager
import uuid
import settings as yajingle_settings

import logging
logger = logging.getLogger("yaapp.yajingle")


class Jingle(models.Model):
    creator = models.ForeignKey(User, verbose_name=_('creator'), related_name='owned_jingles', null=True, blank=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    jtype = models.IntegerField(_('type'), choices=yajingle_settings.JINGLE_TYPE_CHOICES, default=yajingle_settings.JINGLE_TYPE_PRIVATE)
    uuid = models.CharField(_('uuid'), max_length=48)
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    filename = models.CharField(_('filename'), max_length=45)
    duration = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4().hex

        super(Jingle, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


class JingleManager():
    """ Store jingle instances.

    A jingle is::

        jingle = {
            'radio_uuid': radio_uuid,
            'creator': user_id,
            'created': '',
            'updated': '',
            'duration': 120,
            'filename': 'aabbccdd.mp3',
            'name': 'Jingle introduction',
            'description': ''
            'schedule': [{
                'type': 'between_songs',
                'value': 4
            }, {
                'type': 'periodic',
                value: '12h30'
            }, {
                'type': 'periodic',
                value: '18h30'
            }]
        }
    """

    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.jingles
        self.collection.ensure_index("radio_uuid")
        self.collection.ensure_index("uuid")

    def jingle_filepath(self, jingle):
        path = os.path.join(settings.SONGS_ROOT, convert_filename_to_filepath(jingle.get('filename')))
        return path

    def jingle_lq_filepath(self, jingle):
        song_path = os.path.join(settings.SONGS_ROOT, convert_filename_to_filepath(jingle.get('filename')))
        name, extension = os.path.splitext(song_path)
        lq = u'%s_lq%s' % (name, extension)
        return lq

    def notify_scheduler(self, jingle_id, radio_uuid, event_type=TransientRadioHistoryManager.TYPE_JINGLE_UPDATED):
        async_transient_radio_event.delay(event_type=event_type, radio_uuid=radio_uuid, jingle_id=jingle_id)

    def jingles_for_radio(self, radio_uuid):
        return self.collection.find({'radio_uuid': radio_uuid})

    def delete_jingle(self, jingle_id):
        if isinstance(jingle_id, str) or isinstance(jingle_id, unicode):
            jingle_id = ObjectId(jingle_id)
        doc = self.jingle(jingle_id)
        if doc is None:
            return

        fullpath = self.jingle_filepath(doc)
        if fullpath:
            try:
                os.remove(fullpath)
            except:
                pass

        fullpath = self.jingle_lq_filepath(doc)
        if fullpath:
            try:
                os.remove(fullpath)
            except:
                pass

        self.collection.remove({'_id': jingle_id}, safe=True)
        try:
            Jingle.objects.get(uuid=doc.get('uuid')).delete()
        except:
            pass

        radio_uuid = doc.get('radio_uuid')
        if radio_uuid is not None:
            self.notify_scheduler(jingle_id, radio_uuid, event_type=TransientRadioHistoryManager.TYPE_JINGLE_DELETED)

    def jingle(self, jingle_id):
        if isinstance(jingle_id, str) or isinstance(jingle_id, unicode):
            jingle_id = ObjectId(jingle_id)
        return self.collection.find_one({'_id': jingle_id})

    def update_jingle(self, doc):
        self.collection.save(doc, safe=True)
        radio_uuid = doc.get('radio_uuid')
        name = doc.get('name')
        uuid = doc.get('uuid')
        if name is not None and uuid is not None:
            if len(uuid) > 0:
                Jingle.objects.filter(uuid=uuid).update(name=name)

        logger.info('updating jingle %s' % doc)
        if radio_uuid is not None:
            logger.info('notifying scheduler for radio %s' % radio_uuid)
            self.notify_scheduler(doc.get('_id'), radio_uuid, event_type=TransientRadioHistoryManager.TYPE_JINGLE_UPDATED)

    def create_jingle(self, name, radio, creator, description='', filename=None, schedule=None, duration=None):
        jingle = Jingle.objects.create(name=name, filename=filename, description=description, creator=creator, duration=duration)

        doc = {
            'radio_uuid': radio.uuid,
            'uuid': jingle.uuid,
            'creator': jingle.creator.id,
            'filename': filename,
            'created': jingle.created,
            'updated': jingle.updated,
            'name': jingle.name,
            'duration': jingle.duration,
            'description': jingle.description,
            'schedule': schedule
        }
        jingle_id = self.collection.insert(doc, safe=True)
        if radio.uuid is not None:
            self.notify_scheduler(jingle_id, radio.uuid, event_type=TransientRadioHistoryManager.TYPE_JINGLE_ADDED)
        return jingle_id
