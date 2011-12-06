# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing M2M table for field next_songs on 'Radio'
        db.delete_table('yabase_radio_next_songs')

        # Removing M2M table for field wall on 'Radio'
        db.delete_table('yabase_radio_wall')

        # Adding field 'RadioEvent.radio'
        db.add_column('yabase_radioevent', 'radio', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['yabase.Radio']), keep_default=False)


    def backwards(self, orm):
        
        # Adding M2M table for field next_songs on 'Radio'
        db.create_table('yabase_radio_next_songs', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('radio', models.ForeignKey(orm['yabase.radio'], null=False)),
            ('radioevent', models.ForeignKey(orm['yabase.radioevent'], null=False))
        ))
        db.create_unique('yabase_radio_next_songs', ['radio_id', 'radioevent_id'])

        # Adding M2M table for field wall on 'Radio'
        db.create_table('yabase_radio_wall', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('radio', models.ForeignKey(orm['yabase.radio'], null=False)),
            ('radioevent', models.ForeignKey(orm['yabase.radioevent'], null=False))
        ))
        db.create_unique('yabase_radio_wall', ['radio_id', 'radioevent_id'])

        # Deleting field 'RadioEvent.radio'
        db.delete_column('yabase_radioevent', 'radio_id')


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
        'yabase.picture': {
            'Meta': {'object_name': 'Picture'},
            'file': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'yabase.playlist': {
            'CRC': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'Playlist'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'songs': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'songs'", 'symmetrical': 'False', 'to': "orm['yabase.SongInstance']"}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'sync_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'yabase.radio': {
            'Meta': {'object_name': 'Radio'},
            'audience_peak': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'connected_users': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'connected_users'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['yabase.UserProfile']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dislikes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'radio_dislikes'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['yabase.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'likes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'radio_likes'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['yabase.UserProfile']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'overall_listening_time': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.Picture']", 'null': 'True', 'blank': 'True'}),
            'playlists': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'playlists'", 'symmetrical': 'False', 'to': "orm['yabase.Playlist']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'users_with_this_radio_as_favorite': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'users_with_this_radio_as_favorite'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['yabase.UserProfile']"})
        },
        'yabase.radioevent': {
            'Meta': {'object_name': 'RadioEvent'},
            'animated_emoticon': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.Picture']", 'null': 'True', 'blank': 'True'}),
            'radio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.Radio']"}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.SongInstance']", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.UserProfile']", 'null': 'True', 'blank': 'True'})
        },
        'yabase.songinstance': {
            'Meta': {'object_name': 'SongInstance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_play_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'metadata': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['yabase.SongMetadata']", 'unique': 'True'}),
            'play_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'song': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'yasound_score': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'yabase.songmetadata': {
            'Meta': {'object_name': 'SongMetadata'},
            'album_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'artist_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'bpm': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'disc_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'disc_index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [], {}),
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'picture': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.Picture']", 'null': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'track_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'track_index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'yabase.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'bio_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dislikes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'user_dislikes'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['yabase.Radio']"}),
            'facebook_account': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'favorites': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'favorites'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['yabase.Radio']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'join_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_login_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_selection_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'likes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'user_likes'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['yabase.Radio']"}),
            'picture': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.Picture']", 'null': 'True', 'blank': 'True'}),
            'radios': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'radios'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['yabase.Radio']"}),
            'selection': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'selection'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['yabase.Radio']"}),
            'twitter_account': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['yabase']
