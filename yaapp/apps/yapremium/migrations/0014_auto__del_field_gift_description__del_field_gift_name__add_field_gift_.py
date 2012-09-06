# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Gift.description'
        db.delete_column('yapremium_gift', 'description')

        # Deleting field 'Gift.name'
        db.delete_column('yapremium_gift', 'name')

        # Adding field 'Gift.name_en'
        db.add_column('yapremium_gift', 'name_en',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Gift.name_fr'
        db.add_column('yapremium_gift', 'name_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Gift.description_en'
        db.add_column('yapremium_gift', 'description_en',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Gift.description_fr'
        db.add_column('yapremium_gift', 'description_fr',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Subscription.description'
        db.delete_column('yapremium_subscription', 'description')

        # Deleting field 'Subscription.sku'
        db.delete_column('yapremium_subscription', 'sku')

        # Deleting field 'Subscription.name'
        db.delete_column('yapremium_subscription', 'name')

        # Adding field 'Subscription.name_en'
        db.add_column('yapremium_subscription', 'name_en',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Subscription.name_fr'
        db.add_column('yapremium_subscription', 'name_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Subscription.sku_en'
        db.add_column('yapremium_subscription', 'sku_en',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Subscription.sku_fr'
        db.add_column('yapremium_subscription', 'sku_fr',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Subscription.description_en'
        db.add_column('yapremium_subscription', 'description_en',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Subscription.description_fr'
        db.add_column('yapremium_subscription', 'description_fr',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Gift.description'
        db.add_column('yapremium_gift', 'description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Gift.name'
        db.add_column('yapremium_gift', 'name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Deleting field 'Gift.name_en'
        db.delete_column('yapremium_gift', 'name_en')

        # Deleting field 'Gift.name_fr'
        db.delete_column('yapremium_gift', 'name_fr')

        # Deleting field 'Gift.description_en'
        db.delete_column('yapremium_gift', 'description_en')

        # Deleting field 'Gift.description_fr'
        db.delete_column('yapremium_gift', 'description_fr')

        # Adding field 'Subscription.description'
        db.add_column('yapremium_subscription', 'description',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Subscription.sku'
        db.add_column('yapremium_subscription', 'sku',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Subscription.name'
        db.add_column('yapremium_subscription', 'name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Deleting field 'Subscription.name_en'
        db.delete_column('yapremium_subscription', 'name_en')

        # Deleting field 'Subscription.name_fr'
        db.delete_column('yapremium_subscription', 'name_fr')

        # Deleting field 'Subscription.sku_en'
        db.delete_column('yapremium_subscription', 'sku_en')

        # Deleting field 'Subscription.sku_fr'
        db.delete_column('yapremium_subscription', 'sku_fr')

        # Deleting field 'Subscription.description_en'
        db.delete_column('yapremium_subscription', 'description_en')

        # Deleting field 'Subscription.description_fr'
        db.delete_column('yapremium_subscription', 'description_fr')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'yapremium.achievement': {
            'Meta': {'object_name': 'Achievement'},
            'achievement_date': ('django.db.models.fields.DateTimeField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'gift': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yapremium.Gift']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'yapremium.gift': {
            'Meta': {'object_name': 'Gift'},
            'action': ('django.db.models.fields.IntegerField', [], {}),
            'action_url_ios': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_per_user': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'picture_done': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'picture_todo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yapremium.Service']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yapremium.service': {
            'Meta': {'object_name': 'Service'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stype': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yapremium.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'highlighted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['yapremium.Service']", 'symmetrical': 'False'}),
            'sku_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'sku_fr': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'yapremium.userservice': {
            'Meta': {'unique_together': "(('user', 'service'),)", 'object_name': 'UserService'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yapremium.Service']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'yapremium.usersubscription': {
            'Meta': {'object_name': 'UserSubscription'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yapremium.Subscription']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['yapremium']