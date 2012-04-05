# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Device', fields ['user', 'uuid']
        db.delete_unique('account_device', ['user_id', 'uuid'])

        # Deleting field 'Device.uuid'
        db.delete_column('account_device', 'uuid')

        # Adding field 'Device.ios_token'
        db.add_column('account_device', 'ios_token', self.gf('django.db.models.fields.CharField')(default="", max_length=255), keep_default=False)

        # Adding field 'Device.ios_token_type'
        db.add_column('account_device', 'ios_token_type', self.gf('django.db.models.fields.CharField')(default="", max_length=16), keep_default=False)

        # Adding field 'Device.registration_date'
        db.add_column('account_device', 'registration_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2012, 3, 29, 17, 55, 22, 788435), blank=True), keep_default=False)

        # Adding unique constraint on 'Device', fields ['ios_token', 'user']
        db.create_unique('account_device', ['ios_token', 'user_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Device', fields ['ios_token', 'user']
        db.delete_unique('account_device', ['ios_token', 'user_id'])

        # Adding field 'Device.uuid'
        db.add_column('account_device', 'uuid', self.gf('django.db.models.fields.CharField')(default="", max_length=255), keep_default=False)

        # Deleting field 'Device.ios_token'
        db.delete_column('account_device', 'ios_token')

        # Deleting field 'Device.ios_token_type'
        db.delete_column('account_device', 'ios_token_type')

        # Deleting field 'Device.registration_date'
        db.delete_column('account_device', 'registration_date')

        # Adding unique constraint on 'Device', fields ['user', 'uuid']
        db.create_unique('account_device', ['user_id', 'uuid'])


    models = {
        'account.device': {
            'Meta': {'unique_together': "(('user', 'ios_token'),)", 'object_name': 'Device'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ios_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ios_token_type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'registration_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'account.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'account_type': ('django.db.models.fields.CharField', [], {'default': "'yasound'", 'max_length': '20'}),
            'bio_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'facebook_token': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'facebook_uid': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'friends': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'friends_profile'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_authentication_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'picture': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'twitter_token': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'twitter_token_secret': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'twitter_uid': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
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
        }
    }

    complete_apps = ['account']
