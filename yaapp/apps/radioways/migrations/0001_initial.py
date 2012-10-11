# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Continent'
        db.create_table('radioways_continent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('radioways_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('sigle', self.gf('django.db.models.fields.CharField')(max_length=4, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name_uk', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name_es', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name_de', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('radioways', ['Continent'])

        # Adding model 'Country'
        db.create_table('radioways_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('radioways_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('continent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radioways.Continent'])),
            ('sigle', self.gf('django.db.models.fields.CharField')(max_length=4, blank=True)),
            ('name_fr', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name_uk', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name_es', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name_de', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('radioways', ['Country'])

        # Adding model 'Radio'
        db.create_table('radioways_radio', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('radioways_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['radioways.Country'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('rtype', self.gf('django.db.models.fields.IntegerField')()),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('rate_mm', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('logo', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('logo_small', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('stream_url', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('metadata_id', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('bitrate', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('codec', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('stream_response_time', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('radioways', ['Radio'])


    def backwards(self, orm):
        # Deleting model 'Continent'
        db.delete_table('radioways_continent')

        # Deleting model 'Country'
        db.delete_table('radioways_country')

        # Deleting model 'Radio'
        db.delete_table('radioways_radio')


    models = {
        'radioways.continent': {
            'Meta': {'object_name': 'Continent'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_de': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_uk': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'radioways_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'sigle': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'})
        },
        'radioways.country': {
            'Meta': {'object_name': 'Country'},
            'continent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radioways.Continent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_de': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_uk': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'radioways_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'sigle': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'})
        },
        'radioways.radio': {
            'Meta': {'object_name': 'Radio'},
            'bitrate': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'codec': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['radioways.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'logo_small': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'metadata_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'radioways_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'rate_mm': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rtype': ('django.db.models.fields.IntegerField', [], {}),
            'stream_response_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'stream_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['radioways']