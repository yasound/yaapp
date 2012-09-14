# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Country'
        db.create_table('yageoperm_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=4)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
        ))
        db.send_create_signal('yageoperm', ['Country'])

        # Adding model 'GeoFeature'
        db.create_table('yageoperm_geofeature', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yageoperm.Country'])),
            ('feature', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('yageoperm', ['GeoFeature'])

        # Adding unique constraint on 'GeoFeature', fields ['country', 'feature']
        db.create_unique('yageoperm_geofeature', ['country_id', 'feature'])


    def backwards(self, orm):
        # Removing unique constraint on 'GeoFeature', fields ['country', 'feature']
        db.delete_unique('yageoperm_geofeature', ['country_id', 'feature'])

        # Deleting model 'Country'
        db.delete_table('yageoperm_country')

        # Deleting model 'GeoFeature'
        db.delete_table('yageoperm_geofeature')


    models = {
        'yageoperm.country': {
            'Meta': {'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '4'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yageoperm.geofeature': {
            'Meta': {'unique_together': "(('country', 'feature'),)", 'object_name': 'GeoFeature'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yageoperm.Country']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'feature': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['yageoperm']