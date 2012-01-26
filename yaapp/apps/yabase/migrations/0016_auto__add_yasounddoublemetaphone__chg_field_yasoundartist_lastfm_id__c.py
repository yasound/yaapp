# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'YasoundDoubleMetaphone'
        db.create_table(u'yasound_doublemetaphone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('yabase', ['YasoundDoubleMetaphone'])

        # Adding M2M table for field dms on 'YasoundArtist'
        db.create_table(u'yasound_artist_dms', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('yasoundartist', models.ForeignKey(orm['yabase.yasoundartist'], null=False)),
            ('yasounddoublemetaphone', models.ForeignKey(orm['yabase.yasounddoublemetaphone'], null=False))
        ))
        db.create_unique(u'yasound_artist_dms', ['yasoundartist_id', 'yasounddoublemetaphone_id'])

        # Changing field 'YasoundArtist.lastfm_id'
        db.alter_column(u'yasound_artist', 'lastfm_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'YasoundArtist.comment'
        db.alter_column(u'yasound_artist', 'comment', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'YasoundArtist.musicbrainz_id'
        db.alter_column(u'yasound_artist', 'musicbrainz_id', self.gf('django.db.models.fields.CharField')(max_length=36, null=True))

        # Adding M2M table for field dms on 'YasoundAlbum'
        db.create_table(u'yasound_album_dms', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('yasoundalbum', models.ForeignKey(orm['yabase.yasoundalbum'], null=False)),
            ('yasounddoublemetaphone', models.ForeignKey(orm['yabase.yasounddoublemetaphone'], null=False))
        ))
        db.create_unique(u'yasound_album_dms', ['yasoundalbum_id', 'yasounddoublemetaphone_id'])

        # Changing field 'YasoundAlbum.lastfm_id'
        db.alter_column(u'yasound_album', 'lastfm_id', self.gf('django.db.models.fields.CharField')(max_length=20, unique=True, null=True))

        # Changing field 'YasoundAlbum.cover_filename'
        db.alter_column(u'yasound_album', 'cover_filename', self.gf('django.db.models.fields.CharField')(max_length=45, null=True))

        # Changing field 'YasoundAlbum.musicbrainz_id'
        db.alter_column(u'yasound_album', 'musicbrainz_id', self.gf('django.db.models.fields.CharField')(max_length=36, null=True))

        # Adding M2M table for field dms on 'YasoundSong'
        db.create_table(u'yasound_song_dms', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('yasoundsong', models.ForeignKey(orm['yabase.yasoundsong'], null=False)),
            ('yasounddoublemetaphone', models.ForeignKey(orm['yabase.yasounddoublemetaphone'], null=False))
        ))
        db.create_unique(u'yasound_song_dms', ['yasoundsong_id', 'yasounddoublemetaphone_id'])

        # Changing field 'YasoundSong.lastfm_id'
        db.alter_column(u'yasound_song', 'lastfm_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'YasoundSong.comment'
        db.alter_column(u'yasound_song', 'comment', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'YasoundSong.energy'
        db.alter_column(u'yasound_song', 'energy', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2))

        # Changing field 'YasoundSong.lastfm_fingerprint_id'
        db.alter_column(u'yasound_song', 'lastfm_fingerprint_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'YasoundSong.album'
        db.alter_column(u'yasound_song', 'album_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabase.YasoundAlbum'], null=True))

        # Changing field 'YasoundSong.allowed_countries'
        db.alter_column(u'yasound_song', 'allowed_countries', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'YasoundSong.tonality_mode'
        db.alter_column(u'yasound_song', 'tonality_mode', self.gf('django.db.models.fields.SmallIntegerField')(null=True))

        # Changing field 'YasoundSong.echoprint_version'
        db.alter_column(u'yasound_song', 'echoprint_version', self.gf('django.db.models.fields.CharField')(max_length=8, null=True))

        # Changing field 'YasoundSong.musicbrainz_id'
        db.alter_column(u'yasound_song', 'musicbrainz_id', self.gf('django.db.models.fields.CharField')(max_length=36, null=True))

        # Changing field 'YasoundSong.tonality_key'
        db.alter_column(u'yasound_song', 'tonality_key', self.gf('django.db.models.fields.SmallIntegerField')(null=True))

        # Changing field 'YasoundSong.danceability'
        db.alter_column(u'yasound_song', 'danceability', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2))

        # Changing field 'YasoundSong.cover_filename'
        db.alter_column(u'yasound_song', 'cover_filename', self.gf('django.db.models.fields.CharField')(max_length=45, null=True))

        # Changing field 'YasoundSong.tempo'
        db.alter_column(u'yasound_song', 'tempo', self.gf('django.db.models.fields.SmallIntegerField')(null=True))

        # Changing field 'YasoundSong.echonest_id'
        db.alter_column(u'yasound_song', 'echonest_id', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'YasoundSong.fingerprint'
        db.alter_column(u'yasound_song', 'fingerprint', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'YasoundSong.artist'
        db.alter_column(u'yasound_song', 'artist_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['yabase.YasoundArtist'], null=True))

        # Changing field 'YasoundSong.fingerprint_hash'
        db.alter_column(u'yasound_song', 'fingerprint_hash', self.gf('django.db.models.fields.CharField')(max_length=45, null=True))

        # Changing field 'YasoundSong.loudness'
        db.alter_column(u'yasound_song', 'loudness', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2))

        # Adding field 'Radio.anonymous_audience'
        db.add_column('yabase_radio', 'anonymous_audience', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'YasoundDoubleMetaphone'
        db.delete_table(u'yasound_doublemetaphone')

        # Removing M2M table for field dms on 'YasoundArtist'
        db.delete_table('yasound_artist_dms')

        # Changing field 'YasoundArtist.lastfm_id'
        db.alter_column(u'yasound_artist', 'lastfm_id', self.gf('django.db.models.fields.CharField')(default=1, max_length=20))

        # Changing field 'YasoundArtist.comment'
        db.alter_column(u'yasound_artist', 'comment', self.gf('django.db.models.fields.TextField')(default=1))

        # Changing field 'YasoundArtist.musicbrainz_id'
        db.alter_column(u'yasound_artist', 'musicbrainz_id', self.gf('django.db.models.fields.CharField')(default=1, max_length=36))

        # Removing M2M table for field dms on 'YasoundAlbum'
        db.delete_table('yasound_album_dms')

        # Changing field 'YasoundAlbum.lastfm_id'
        db.alter_column(u'yasound_album', 'lastfm_id', self.gf('django.db.models.fields.CharField')(default=1, max_length=20, unique=True))

        # Changing field 'YasoundAlbum.cover_filename'
        db.alter_column(u'yasound_album', 'cover_filename', self.gf('django.db.models.fields.CharField')(default=1, max_length=45))

        # Changing field 'YasoundAlbum.musicbrainz_id'
        db.alter_column(u'yasound_album', 'musicbrainz_id', self.gf('django.db.models.fields.CharField')(default=1, max_length=36))

        # Removing M2M table for field dms on 'YasoundSong'
        db.delete_table('yasound_song_dms')

        # Changing field 'YasoundSong.lastfm_id'
        db.alter_column(u'yasound_song', 'lastfm_id', self.gf('django.db.models.fields.CharField')(default=1, max_length=20))

        # Changing field 'YasoundSong.comment'
        db.alter_column(u'yasound_song', 'comment', self.gf('django.db.models.fields.TextField')(default=1))

        # Changing field 'YasoundSong.energy'
        db.alter_column(u'yasound_song', 'energy', self.gf('django.db.models.fields.DecimalField')(default=1, max_digits=10, decimal_places=2))

        # Changing field 'YasoundSong.lastfm_fingerprint_id'
        db.alter_column(u'yasound_song', 'lastfm_fingerprint_id', self.gf('django.db.models.fields.CharField')(default=1, max_length=20))

        # Changing field 'YasoundSong.album'
        db.alter_column(u'yasound_song', 'album_id', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['yabase.YasoundAlbum']))

        # Changing field 'YasoundSong.allowed_countries'
        db.alter_column(u'yasound_song', 'allowed_countries', self.gf('django.db.models.fields.CharField')(default=1, max_length=255))

        # Changing field 'YasoundSong.tonality_mode'
        db.alter_column(u'yasound_song', 'tonality_mode', self.gf('django.db.models.fields.SmallIntegerField')(default=1))

        # Changing field 'YasoundSong.echoprint_version'
        db.alter_column(u'yasound_song', 'echoprint_version', self.gf('django.db.models.fields.CharField')(default=1, max_length=8))

        # Changing field 'YasoundSong.musicbrainz_id'
        db.alter_column(u'yasound_song', 'musicbrainz_id', self.gf('django.db.models.fields.CharField')(default=1, max_length=36))

        # Changing field 'YasoundSong.tonality_key'
        db.alter_column(u'yasound_song', 'tonality_key', self.gf('django.db.models.fields.SmallIntegerField')(default=1))

        # Changing field 'YasoundSong.danceability'
        db.alter_column(u'yasound_song', 'danceability', self.gf('django.db.models.fields.DecimalField')(default=1, max_digits=10, decimal_places=2))

        # Changing field 'YasoundSong.cover_filename'
        db.alter_column(u'yasound_song', 'cover_filename', self.gf('django.db.models.fields.CharField')(default=1, max_length=45))

        # Changing field 'YasoundSong.tempo'
        db.alter_column(u'yasound_song', 'tempo', self.gf('django.db.models.fields.SmallIntegerField')(default=1))

        # Changing field 'YasoundSong.echonest_id'
        db.alter_column(u'yasound_song', 'echonest_id', self.gf('django.db.models.fields.CharField')(default=1, max_length=20))

        # Changing field 'YasoundSong.fingerprint'
        db.alter_column(u'yasound_song', 'fingerprint', self.gf('django.db.models.fields.TextField')(default=1))

        # Changing field 'YasoundSong.artist'
        db.alter_column(u'yasound_song', 'artist_id', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['yabase.YasoundArtist']))

        # Changing field 'YasoundSong.fingerprint_hash'
        db.alter_column(u'yasound_song', 'fingerprint_hash', self.gf('django.db.models.fields.CharField')(default=1, max_length=45))

        # Changing field 'YasoundSong.loudness'
        db.alter_column(u'yasound_song', 'loudness', self.gf('django.db.models.fields.DecimalField')(default=1, max_digits=10, decimal_places=2))

        # Deleting field 'Radio.anonymous_audience'
        db.delete_column('yabase_radio', 'anonymous_audience')


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
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
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
            'anonymous_audience': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'audience_peak': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'computing_next_songs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owned_radios'", 'null': 'True', 'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'genre': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'next_songs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['yabase.SongInstance']", 'through': "orm['yabase.NextSong']", 'symmetrical': 'False'}),
            'overall_listening_time': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'playlists': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'playlists'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['yabase.Playlist']"}),
            'ready': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'theme': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'through': "orm['yabase.RadioUser']", 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '48', 'blank': 'True'})
        },
        'yabase.radiouser': {
            'Meta': {'unique_together': "(('radio', 'user'),)", 'object_name': 'RadioUser'},
            'connected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'favorite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listening': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'end_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'radio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.Radio']"}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.SongInstance']", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'yabase.yasoundalbum': {
            'Meta': {'object_name': 'YasoundAlbum', 'db_table': "u'yasound_album'"},
            'cover_filename': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'dms': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['yabase.YasoundDoubleMetaphone']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'lastfm_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'musicbrainz_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name_simplified': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'yabase.yasoundartist': {
            'Meta': {'object_name': 'YasoundArtist', 'db_table': "u'yasound_artist'"},
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dms': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['yabase.YasoundDoubleMetaphone']", 'null': 'True', 'blank': 'True'}),
            'echonest_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'lastfm_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'musicbrainz_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name_simplified': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'yabase.yasounddoublemetaphone': {
            'Meta': {'object_name': 'YasoundDoubleMetaphone', 'db_table': "u'yasound_doublemetaphone'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'yabase.yasoundgenre': {
            'Meta': {'object_name': 'YasoundGenre', 'db_table': "u'yasound_genre'"},
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'namecanonical': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '45'})
        },
        'yabase.yasoundsong': {
            'Meta': {'object_name': 'YasoundSong', 'db_table': "u'yasound_song'"},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.YasoundAlbum']", 'null': 'True', 'blank': 'True'}),
            'album_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'album_name_simplified': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'allowed_countries': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'artist': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.YasoundArtist']", 'null': 'True', 'blank': 'True'}),
            'artist_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'artist_name_simplified': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'cover_filename': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'danceability': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'dms': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['yabase.YasoundDoubleMetaphone']", 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'echonest_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'echoprint_version': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'energy': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'filesize': ('django.db.models.fields.IntegerField', [], {}),
            'fingerprint': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fingerprint_hash': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'lastfm_fingerprint_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'lastfm_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'loudness': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'musicbrainz_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name_simplified': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'publish_at': ('django.db.models.fields.DateTimeField', [], {}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tempo': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tonality_key': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tonality_mode': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'yabase.yasoundsonggenre': {
            'Meta': {'object_name': 'YasoundSongGenre', 'db_table': "u'yasound_song_genre'"},
            'genre': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.YasoundGenre']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['yabase.YasoundSong']"})
        }
    }

    complete_apps = ['yabase']
