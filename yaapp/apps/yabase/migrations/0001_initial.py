# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Picture'
        db.create_table('yabase_picture', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('yabase', ['Picture'])

        # Adding model 'SongMetadata'
        db.create_table('yabase_songmetadata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('artist_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('album_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('track_index', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('track_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('disc_index', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('disc_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('bpm', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.FloatField')()),
            ('genre', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('picture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabase.Picture'], null=True, blank=True)),
        ))
        db.send_create_signal('yabase', ['SongMetadata'])

        # Adding model 'SongInstance'
        db.create_table('yabase_songinstance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('song', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('play_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_play_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('yasound_score', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('metadata', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['yabase.SongMetadata'], unique=True)),
        ))
        db.send_create_signal('yabase', ['SongInstance'])

        # Adding model 'Playlist'
        db.create_table('yabase_playlist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sync_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('CRC', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('yabase', ['Playlist'])

        # Adding M2M table for field songs on 'Playlist'
        db.create_table('yabase_playlist_songs', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('playlist', models.ForeignKey(orm['yabase.playlist'], null=False)),
            ('songinstance', models.ForeignKey(orm['yabase.songinstance'], null=False))
        ))
        db.create_unique('yabase_playlist_songs', ['playlist_id', 'songinstance_id'])

        # Adding model 'Radio'
        db.create_table('yabase_radio', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='owned_radios', unique=True, null=True, to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('picture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabase.Picture'], null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('audience_peak', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('overall_listening_time', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('yabase', ['Radio'])

        # Adding M2M table for field playlists on 'Radio'
        db.create_table('yabase_radio_playlists', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('radio', models.ForeignKey(orm['yabase.radio'], null=False)),
            ('playlist', models.ForeignKey(orm['yabase.playlist'], null=False))
        ))
        db.create_unique('yabase_radio_playlists', ['radio_id', 'playlist_id'])

        # Adding model 'RadioUser'
        db.create_table('yabase_radiouser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('radio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabase.Radio'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('mood', self.gf('django.db.models.fields.CharField')(default='L', max_length=1)),
            ('favorite', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('connected', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('radio_selected', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('yabase', ['RadioUser'])

        # Adding unique constraint on 'RadioUser', fields ['radio', 'user']
        db.create_unique('yabase_radiouser', ['radio_id', 'user_id'])

        # Adding model 'WallEvent'
        db.create_table('yabase_wallevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('radio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabase.Radio'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabase.SongInstance'], null=True, blank=True)),
            ('old_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('animated_emoticon', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('picture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabase.Picture'], null=True, blank=True)),
        ))
        db.send_create_signal('yabase', ['WallEvent'])

        # Adding model 'NextSong'
        db.create_table('yabase_nextsong', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('radio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabase.Radio'])),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabase.SongInstance'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('yabase', ['NextSong'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'RadioUser', fields ['radio', 'user']
        db.delete_unique('yabase_radiouser', ['radio_id', 'user_id'])

        # Deleting model 'Picture'
        db.delete_table('yabase_picture')

        # Deleting model 'SongMetadata'
        db.delete_table('yabase_songmetadata')

        # Deleting model 'SongInstance'
        db.delete_table('yabase_songinstance')

        # Deleting model 'Playlist'
        db.delete_table('yabase_playlist')

        # Removing M2M table for field songs on 'Playlist'
        db.delete_table('yabase_playlist_songs')

        # Deleting model 'Radio'
        db.delete_table('yabase_radio')

        # Removing M2M table for field playlists on 'Radio'
        db.delete_table('yabase_radio_playlists')

        # Deleting model 'RadioUser'
        db.delete_table('yabase_radiouser')

        # Deleting model 'WallEvent'
        db.delete_table('yabase_wallevent')

        # Deleting model 'NextSong'
        db.delete_table('yabase_nextsong')


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
        'yabase.nextsong': {
            'Meta': {'object_name': 'NextSong'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'radio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.Radio']"}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.SongInstance']"})
        },
        'yabase.picture': {
            'Meta': {'object_name': 'Picture'},
            'file': ('django.db.models.fields.IntegerField', [], {}),
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
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'owned_radios'", 'unique': 'True', 'null': 'True', 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'next_songs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['yabase.SongInstance']", 'through': "orm['yabase.NextSong']", 'symmetrical': 'False'}),
            'overall_listening_time': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.Picture']", 'null': 'True', 'blank': 'True'}),
            'playlists': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'playlists'", 'symmetrical': 'False', 'to': "orm['yabase.Playlist']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'through': "orm['yabase.RadioUser']", 'blank': 'True'})
        },
        'yabase.radiouser': {
            'Meta': {'unique_together': "(('radio', 'user'),)", 'object_name': 'RadioUser'},
            'connected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'favorite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mood': ('django.db.models.fields.CharField', [], {'default': "'L'", 'max_length': '1'}),
            'radio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.Radio']"}),
            'radio_selected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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
        'yabase.wallevent': {
            'Meta': {'object_name': 'WallEvent'},
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['yabase']
