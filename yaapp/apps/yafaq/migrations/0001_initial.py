# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FaqEntry'
        db.create_table('yafaq_faqentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title_en', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('title_fr', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
            ('content_en', self.gf('django.db.models.fields.TextField')()),
            ('content_fr', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('yafaq', ['FaqEntry'])


    def backwards(self, orm):
        # Deleting model 'FaqEntry'
        db.delete_table('yafaq_faqentry')


    models = {
        'yafaq.faqentry': {
            'Meta': {'ordering': "['order']", 'object_name': 'FaqEntry'},
            'content_en': ('django.db.models.fields.TextField', [], {}),
            'content_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'title_fr': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['yafaq']