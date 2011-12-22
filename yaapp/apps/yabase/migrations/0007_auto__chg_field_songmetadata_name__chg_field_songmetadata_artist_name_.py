# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'SongMetadata.name'
        db.alter_column('yabase_songmetadata', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'SongMetadata.artist_name'
        db.alter_column('yabase_songmetadata', 'artist_name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'SongMetadata.album_name'
        db.alter_column('yabase_songmetadata', 'album_name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'SongMetadata.genre'
        db.alter_column('yabase_songmetadata', 'genre', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Playlist.name'
        db.alter_column('yabase_playlist', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Playlist.source'
        db.alter_column('yabase_playlist', 'source', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Radio.name'
        db.alter_column('yabase_radio', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Radio.theme'
        db.alter_column('yabase_radio', 'theme', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Radio.genre'
        db.alter_column('yabase_radio', 'genre', self.gf('django.db.models.fields.CharField')(max_length=255))


    def backwards(self, orm):
        
        # Changing field 'SongMetadata.name'
        db.alter_column('yabase_songmetadata', 'name', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Changing field 'SongMetadata.artist_name'
        db.alter_column('yabase_songmetadata', 'artist_name', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Changing field 'SongMetadata.album_name'
        db.alter_column('yabase_songmetadata', 'album_name', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Changing field 'SongMetadata.genre'
        db.alter_column('yabase_songmetadata', 'genre', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Changing field 'Playlist.name'
        db.alter_column('yabase_playlist', 'name', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Changing field 'Playlist.source'
        db.alter_column('yabase_playlist', 'source', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Changing field 'Radio.name'
        db.alter_column('yabase_radio', 'name', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Changing field 'Radio.theme'
        db.alter_column('yabase_radio', 'theme', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Changing field 'Radio.genre'
        db.alter_column('yabase_radio', 'genre', self.gf('django.db.models.fields.CharField')(max_length=128))


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
        'yabase.playlist': {
            'CRC': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'Playlist'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sync_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        'yabase.radio': {
            'Meta': {'object_name': 'Radio'},
            'audience_peak': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_radios'", 'null': 'True', 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'next_songs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['yabase.SongInstance']", 'through': "orm['yabase.NextSong']", 'symmetrical': 'False'}),
            'overall_listening_time': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'playlists': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'playlists'", 'symmetrical': 'False', 'to': "orm['yabase.Playlist']"}),
            'theme': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'through': "orm['yabase.RadioUser']", 'blank': 'True'})
        },
        'yabase.radiouser': {
            'Meta': {'unique_together': "(('radio', 'user'),)", 'object_name': 'RadioUser'},
            'connected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'favorite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mood': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'radio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.Radio']"}),
            'radio_selected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'yabase.songinstance': {
            'Meta': {'object_name': 'SongInstance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_play_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'metadata': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.SongMetadata']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'play_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'playlist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.Playlist']"}),
            'song': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'through': "orm['yabase.SongUser']", 'blank': 'True'}),
            'yasound_score': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'yabase.songmetadata': {
            'Meta': {'object_name': 'SongMetadata'},
            'album_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'artist_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'bpm': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'disc_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'disc_index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'track_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'track_index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'yabase.songuser': {
            'Meta': {'unique_together': "(('song', 'user'),)", 'object_name': 'SongUser'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mood': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.SongInstance']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'yabase.wallevent': {
            'Meta': {'object_name': 'WallEvent'},
            'animated_emoticon': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'radio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.Radio']"}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.SongInstance']", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'yabase.yasoundalbum': {
            'Meta': {'object_name': 'YasoundAlbum', 'db_table': "u'yasound_album'"},
            'cover_filename': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'lastfm_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'musicbrainz_id': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name_simplified': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'yabase.yasoundartist': {
            'Meta': {'object_name': 'YasoundArtist', 'db_table': "u'yasound_artist'"},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'echonest_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'lastfm_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'musicbrainz_id': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name_simplified': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'yabase.yasoundgenre': {
            'Meta': {'object_name': 'YasoundGenre', 'db_table': "u'yasound_genre'"},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'namecanonical': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '45'})
        },
        'yabase.yasoundsong': {
            'Meta': {'object_name': 'YasoundSong', 'db_table': "u'yasound_song'"},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.YasoundAlbum']"}),
            'album_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'album_name_simplified': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'allowed_countries': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.YasoundArtist']"}),
            'artist_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'artist_name_simplified': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'cover_filename': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'danceability': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'echonest_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'echoprint_version': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'energy': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'filesize': ('django.db.models.fields.IntegerField', [], {}),
            'fingerprint': ('django.db.models.fields.TextField', [], {}),
            'fingerprint_hash': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'lastfm_fingerprint_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'lastfm_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'loudness': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'musicbrainz_id': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name_simplified': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'publish_at': ('django.db.models.fields.DateTimeField', [], {}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tempo': ('django.db.models.fields.SmallIntegerField', [], {}),
            'tonality_key': ('django.db.models.fields.SmallIntegerField', [], {}),
            'tonality_mode': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'yabase.yasoundsonggenre': {
            'Meta': {'object_name': 'YasoundSongGenre', 'db_table': "u'yasound_song_genre'"},
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.YasoundGenre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.YasoundSong']"})
        }
    }

    complete_apps = ['yabase']
