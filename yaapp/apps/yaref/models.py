"""
Contains models related to yasound database (ie all the songs)
"""
from django.conf import settings
from django.db import models
from django.db.models import Q
from fuzzywuzzy import fuzz
from sorl.thumbnail import get_thumbnail
from uploader import lastfm
import buylink
import django.db.models.options as options
import logging
import musicbrainzngs
from tempfile import mkdtemp
import os, errno
import shutil
import string
import utils as yaref_utils
import yasearch.indexer as yasearch_indexer
import yasearch.search as yasearch_search
import yasearch.utils as yasearch_utils
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger("yaapp.yaref")


if not 'db_name' in options.DEFAULT_NAMES:
    options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('db_name',)


class YasoundArtist(models.Model):
    echonest_id = models.CharField(unique=True, max_length=20)
    lastfm_id = models.CharField(max_length=20, blank=True, null=True)
    musicbrainz_id = models.CharField(max_length=36, blank=True, null=True)
    name = models.CharField(max_length=255)

    name_simplified = models.CharField(max_length=255)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        db_table = u'yasound_artist'
        db_name = u'yasound'

    def __unicode__(self):
        return self.name


class YasoundAlbum(models.Model):
    lastfm_id = models.CharField(unique=True, max_length=20, null=True, blank=True)
    musicbrainz_id = models.CharField(max_length=36, blank=True, null=True)
    name = models.CharField(max_length=255)
    name_simplified = models.CharField(max_length=255)
    cover_filename = models.CharField(max_length=45, null=True, blank=True)

    def has_cover(self):
        if self.cover_filename is None or len(self.cover_filename) == 0:
            return False
        return True

    @property
    def cover_url(self):
        if not self.cover_filename:
            return None
        short_url = '%s%s' % (settings.ALBUM_COVER_SHORT_URL,
                              yaref_utils.convert_filename_to_filepath(self.cover_filename))
        print short_url
        try:
            return get_thumbnail(short_url, '64x64', crop='center').url
        except:
            return None

    @property
    def large_cover_url(self):
        if not self.cover_filename:
            return None
        short_url = '%s%s' % (settings.ALBUM_COVER_SHORT_URL,
                              yaref_utils.convert_filename_to_filepath(self.cover_filename))
        try:
            return get_thumbnail(short_url, '256x256', crop='center').url
        except:
            return None

    def custom_cover_url(self, size='64x64'):
        url = None
        if not self.cover_filename:
            url = get_thumbnail(settings.DEFAULT_TRACK_IMAGE_PATH, size, crop='center', format='JPEG', quality=90).url
        else:
            short_url = '%s%s' % (settings.ALBUM_COVER_SHORT_URL,
                                  yaref_utils.convert_filename_to_filepath(self.cover_filename))
            try:
                url = get_thumbnail(short_url, size, crop='center', format='JPEG', quality=90).url
            except:
                pass
        return url

    def set_cover(self, data, extension, replace=True):
        has_cover = self.has_cover()
        logger.debug('%s has cover ? %s' % (self.id, has_cover))
        if has_cover and not replace:
            return

        filename = ''
        if has_cover:
            filename = self.cover_filename
            path = os.path.join(settings.ALBUM_COVERS_ROOT, yaref_utils.convert_filename_to_filepath(filename))
        else:
            filename, path = yaref_utils.generate_filename_and_path_for_album_cover(extension)

        logger.debug('filename=%s, path=%s' % (filename, path))
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        with open(path, 'wb') as img:
            img.write(data)
            self.cover_filename = filename
            self.save()

    class Meta:
        db_table = u'yasound_album'
        db_name = u'yasound'

    def __unicode__(self):
        return self.name


class YasoundGenre(models.Model):
    name = models.CharField(max_length=45)
    name_canonical = models.CharField(unique=True, max_length=45)

    class Meta:
        db_table = u'yasound_genre'
        db_name = u'yasound'

    def __unicode__(self):
        return self.name


class YasoundSongManager(models.Manager):

    _max_query = 0
    _max_song = None

    def test_fuzzy(self, limit=5):
        import random
        from time import time
        count = 100
        random_ids = random.sample(xrange(1600000), count)
        artist_records = list(YasoundSong.objects.filter(id__in=random_ids).all())

        found = 0
        errors = 0
        start = time()
        for i, artist in enumerate(artist_records):
            res = self.find_fuzzy(artist.name, artist.album_name, artist.artist_name, limit=limit)
            if res:
                found += 1
                if res["db_id"] != artist.id:
                    if res["name"] != artist.name or res["artist"] != artist.artist_name or res["album"] != artist.album_name:
                        logger.debug("** error : %d instead of %d" % (res['db_id'], artist.id))
                        logger.debug("** wrong = %s|%s|%s" % (res["name"], res["album"], res["artist"]))
                        logger.debug("** real  = %s|%s|%s" % (artist.name, artist.album_name, artist.artist_name))
                        errors += 1
                        found -= 1
        elapsed = time() - start
        logger.debug('Complete search took ' + str(elapsed) + ' seconds')
        logger.debug('Mean : ' + str(elapsed / count) + ' seconds')
        logger.debug(
            'Found : %d/%d (%d%%), errors = %d (%d%%)' % (found, count, 100 * found / count, errors, 100 * errors / count))
        if self._max_song:
            song = self.get(id=self._max_song['db_id'])
            logger.debug('slowest song : %d:%s|%s|%s (%f)' % (song.id,
                                                              song.name,
                                                              song.album_name,
                                                              song.artist_name,
                                                              self._max_query))

    def last_indexed(self):
        doc = yasearch_indexer.get_last_song_doc()
        if doc and doc.count() > 0:
            return self.get(id=doc[0]['db_id'])
        return None

    def _is_probably_cover_or_karaoke(self, s):
        if 'karaoke' in s:
            return True
        if 'cover' in s:
            return True
        if 'covers' in s:
            return True
        if 'reprise' in s:
            return True
        if 'reprises' in s:
            return True
        if 'tribute' in s:
            return True
        if 'hommage' in s:
            return True

    def _check_candidates(self, songs, name, album, artist):
        best_ratio = 0
        best_song = None

        name_is_probably_cover_or_karaoke = self._is_probably_cover_or_karaoke(name)
        album_is_probably_cover_or_karaoke = self._is_probably_cover_or_karaoke(album)
        artist_is_probably_cover_or_karaoke = self._is_probably_cover_or_karaoke(artist)

        for song in songs:
            ratio_song, ratio_album, ratio_artist = 0, 0, 0

            if name is not None and song["name"] is not None:
                ratio_song = fuzz.token_sort_ratio(name, song["name"])

                if not name_is_probably_cover_or_karaoke and self._is_probably_cover_or_karaoke(song['name']):
                    ratio_song -= 20

            if album is not None and song["album"] is not None:
                ratio_album = fuzz.token_sort_ratio(album, song["album"])

                if not album_is_probably_cover_or_karaoke and self._is_probably_cover_or_karaoke(song['album']):
                    ratio_album -= 20

            if artist is not None and song["artist"] is not None:
                ratio_artist = fuzz.token_sort_ratio(artist, song["artist"])
                if not artist_is_probably_cover_or_karaoke and self._is_probably_cover_or_karaoke(song['artist']):
                    ratio_artist -= 20

            ratio = ratio_song + ratio_album / 4 + ratio_artist / 4
            if ratio >= best_ratio and ratio > 60:
                best_ratio = ratio
                best_song = song
        return best_song, best_ratio

    def find_fuzzy(self, name, album, artist, limit=5):
        from time import time
        start = time()
        songs = yasearch_search.find_song(name, album, artist, remove_common_words=True)
        song, ratio = self._check_candidates(songs, name, album, artist)
        elapsed = time() - start
        if not song:
            logger.debug('find fuzzy: %s|%s|%s : FAILED in %s seconds' % (name, album, artist, str(elapsed)))
        else:
            logger.debug('find fuzzy: %s|%s|%s : OK in %s seconds' % (name, album, artist, str(elapsed)))
        if elapsed > self._max_query:
            self._max_query = elapsed
            self._max_song = song
        return song

    def search_fuzzy(self, search_text, limit=25, exclude_song_ids=[]):
        print 'search fuzzy "%s"' % search_text
        songs = yasearch_search.search_song(search_text, remove_common_words=True, exclude_ids=exclude_song_ids)
        results = []
        if not search_text:
            return results

        for s in songs:
            song_info_list = []
            if s["name"] is not None:
                song_info_list.append(s["name"])
            if s["album"] is not None:
                song_info_list.append(s["album"])
            if s["artist"] is not None:
                song_info_list.append(s["artist"])
            song_info = string.join(song_info_list)
            ratio = yasearch_utils.token_set_ratio(search_text.lower(), song_info.lower(), method='mean')
            res = (s, ratio)
            results.append(res)

        sorted_results = sorted(results, key=lambda r: r[1], reverse=True)
        return sorted_results[:limit]

    def search(self, search_text, offset=0, count=25, tolerance=0.75):
        limit = offset + count

        songs = list(self.filter(Q(name_simplified__iexact=search_text) | Q(
            artist_name_simplified__iexact=search_text) | Q(album_name_simplified__iexact=search_text)))
        exact_count = len(songs)

        if exact_count < limit:
            exclude_ids = []
            for s in songs:
                exclude_ids.append(s.id)

            fuzzy_limit = limit - exact_count
            res = self.search_fuzzy(search_text, fuzzy_limit, exclude_song_ids=exclude_ids)
            best_score = None
            for i in res:
                song_id = i[0]["db_id"]
                score = i[1]
                if not best_score:
                    best_score = score
                if score < best_score * tolerance:
                    break
                songs.append(YasoundSong.objects.get(id=song_id))

        final_songs = songs[offset:offset + count]
        return final_songs

    def get_cover_url(self, filename, size='64x64'):
        url = '%s%s' % (settings.SONG_COVER_SHORT_URL,
                        yaref_utils.convert_filename_to_filepath(filename))
        try:
            return get_thumbnail(url, size, crop='center').url
        except:
            url = '%s%s' % (settings.ALBUM_COVER_SHORT_URL,
                            yaref_utils.convert_filename_to_filepath(filename))
            try:
                return get_thumbnail(url, size, crop='center').url
            except:
                return None
        return None


class YasoundSong(models.Model):
    """A song, associated with mp3 file.

    """

    objects = YasoundSongManager()
    artist = models.ForeignKey(YasoundArtist, null=True, blank=True, on_delete=models.SET_NULL)
    album = models.ForeignKey(YasoundAlbum, null=True, blank=True, on_delete=models.SET_NULL)
    echonest_id = models.CharField(max_length=20, blank=True, null=True)
    lastfm_id = models.CharField(max_length=20, blank=True, null=True)
    lastfm_fingerprint_id = models.CharField(max_length=20, blank=True, null=True)
    musicbrainz_id = models.CharField(max_length=36, blank=True, null=True)
    filename = models.CharField(max_length=45)
    filesize = models.IntegerField()
    name = models.CharField(max_length=255)
    name_simplified = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255, null=True, blank=True)
    artist_name_simplified = models.CharField(max_length=255, null=True, blank=True)
    album_name = models.CharField(max_length=255, null=True, blank=True)
    album_name_simplified = models.CharField(max_length=255, null=True, blank=True)
    duration = models.IntegerField()
    danceability = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    loudness = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    energy = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tempo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tonality_mode = models.SmallIntegerField(null=True, blank=True)
    tonality_key = models.SmallIntegerField(null=True, blank=True)
    fingerprint = models.TextField(null=True, blank=True)
    fingerprint_hash = models.CharField(max_length=45, null=True, blank=True)
    echoprint_version = models.CharField(max_length=8, null=True, blank=True)
    publish_at = models.DateTimeField(blank=True, null=True)
    published = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    allowed_countries = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    cover_filename = models.CharField(max_length=45, blank=True, null=True)
    quality = models.SmallIntegerField(blank=True, null=True)
    owner_id = models.IntegerField(blank=True, null=True)

    def generate_buy_link(self):
        return buylink.generate_buy_link(self.name, self.album_name, self.artist_name)

    @property
    def cover_url(self):
        if not self.cover_filename:
            return None
        short_url = '%s%s' % (settings.SONG_COVER_SHORT_URL,
                              yaref_utils.convert_filename_to_filepath(self.cover_filename))
        try:
            return get_thumbnail(short_url, '64x64', crop='center').url
        except:
            return None

    @property
    def large_cover_url(self):
        if not self.cover_filename:
            return None
        short_url = '%s%s' % (settings.SONG_COVER_SHORT_URL,
                              yaref_utils.convert_filename_to_filepath(self.cover_filename))
        try:
            return get_thumbnail(short_url, '256x256', crop='center').url
        except:
            return None

    def custom_cover_url(self, size='64x64'):
        url = None
        if not self.cover_filename:
            url = get_thumbnail(settings.DEFAULT_TRACK_IMAGE_PATH, size, crop='center', format='JPEG', quality=90).url
        else:
            short_url = '%s%s' % (settings.SONG_COVER_SHORT_URL,
                                  yaref_utils.convert_filename_to_filepath(self.cover_filename))
            try:
                url = get_thumbnail(short_url, size, crop='center', format='JPEG', quality=90).url
            except:
                pass
        return url

    def has_cover(self):
        """return True if song has a non-generic cover"""

        if not self.cover_filename:
            return False
        return True

    @property
    def title(self):
        name = self.name
        artist_name = self.artist_name
        album_name = self.album_name

        if name == '':
            name = _('Unknown song')
        if album_name == '':
            album_name = _('Unknown artist')

        if album_name != '':
            return u'%s %s %s %s %s' % (name, _('by'), artist_name, _('on'), album_name)
        else:
            return u'%s %s %s' % (name, _('by'), artist_name)

    def as_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'name_simplified': self.name_simplified,
            'album': self.album_name,
            'album_simplified': self.album_name_simplified,
            'artist': self.artist_name,
            'artist_simplified': self.artist_name_simplified,
            'filesize': self.filesize
        }
        return data

    def build_fuzzy_index(self, upsert=False, insert=True):
        return yasearch_indexer.add_song(self, upsert, insert)

    def get_song_path(self):
        return os.path.join(settings.SONGS_ROOT, yaref_utils.convert_filename_to_filepath(self.filename))

    def get_song_preview_path(self):
        song_path = os.path.join(settings.SONGS_ROOT, yaref_utils.convert_filename_to_filepath(self.filename))
        name, extension = os.path.splitext(song_path)
        preview = u'%s_preview64%s' % (name, extension)
        return preview

    def get_song_hq_path(self):
        return os.path.join(settings.SONGS_ROOT, yaref_utils.convert_filename_to_filepath(self.filename))

    def get_song_lq_path(self):
        song_path = os.path.join(settings.SONGS_ROOT, yaref_utils.convert_filename_to_filepath(self.filename))
        name, extension = os.path.splitext(song_path)
        lq = u'%s_lq%s' % (name, extension)
        return lq

    def get_song_lq_relative_path(self):
        song_path = yaref_utils.convert_filename_to_filepath(self.filename)
        name, extension = os.path.splitext(song_path)
        lq = u'%s_lq%s' % (name, extension)
        return lq

    def get_song_hq_relative_path(self):
        song_path = yaref_utils.convert_filename_to_filepath(self.filename)
        return song_path

    def find_lastfm_fingerprintid(self):
        song_path = os.path.join(settings.SONGS_ROOT, yaref_utils.convert_filename_to_filepath(self.filename))
        return lastfm.find_fingerprintid(song_path)

    def find_lastfm_rank(self):
        fingerprintid = self.lastfm_fingerprint_id
        if fingerprintid is None:
            fingerprintid = self.find_lastfm_fingerprintid()
            if fingerprintid:
                self.lastfm_fingerprint_id = fingerprintid
                self.save()

        if not fingerprintid:
            return None

        rank = 0.0
        try:
            rank = float(lastfm.find_rank(fingerprintid))
        except:
            pass
        return rank

    def find_mbid(self):
        name, artist, mbid = self.name, self.artist_name, self.musicbrainz_id
        if mbid is None or len(mbid) == 0:
            metadata, valid = lastfm.find_by_name_artist(name=name, artist=artist)
            if valid and metadata.get('id') == self.lastfm_id:
                mbid = metadata.get('mbid')
                return mbid
        return None

    def _lastfm_data(self):
        name, artist, mbid = self.name, self.artist_name, self.musicbrainz_id
        valid = False
        metadata = []
        if mbid is not None and mbid > 0:
            metadata, valid = lastfm.find_by_mbid(mbid=mbid)
        else:
            metadata, valid = lastfm.find_by_name_artist(name=name, artist=artist)

        s = None
        if valid and self.lastfm_id and metadata.get('id') == self.lastfm_id:
            s = {
                'name': metadata.get('name'),
                'artist': metadata.get('artist'),
                'album': metadata.get('album'),
            }
        return s

    def _musicbrainz_data(self):
        musicbrainzngs.set_useragent("Yasound", "0.1", "https://yasound.com")
        s = None
        mbid = self.musicbrainz_id
        if not mbid:
            return s

        name, album, artist = '', '', ''
        try:
            data = musicbrainzngs.get_recording_by_id(mbid, includes=['artists', 'releases'])
            artist = data.get('recording').get('artist-credit')[0].get('artist').get('name')
            album = data.get('recording').get('release-list')[0].get('title')
            name = data.get('recording').get('title')
        except:
            pass

        if name != '' or artist != '' or album != '':
            s = {
                'name': name,
                'album': album,
                'artist': artist
            }
        return s

    def find_synonyms(self):
        name, artist, album = self.name, self.artist_name, self.album_name
        name = name.lower() if name is not None else ''
        artist = artist.lower() if artist is not None else ''
        album = album.lower() if album is not None else ''

        synonyms = []

        lastfm_data = self._lastfm_data()
        if lastfm_data:
            if lastfm_data['name'].lower() != name \
                or lastfm_data['artist'].lower() != artist \
                    or lastfm_data['album'].lower() != album:
                synonyms.append(lastfm_data)

        musicbrainz_data = self._musicbrainz_data()
        if musicbrainz_data:
            if musicbrainz_data['name'].lower() != name \
                or musicbrainz_data['artist'].lower() != artist \
                    or musicbrainz_data['album'].lower() != album:
                synonyms.append(musicbrainz_data)

        return synonyms

    def find_backup_path(self):
        song_path = self.get_song_path()
        name, extension = os.path.splitext(song_path)
        backup_path = u'%s_quarantine%s' % (name, extension)
        path_exists = os.path.exists(backup_path)
        i = 0
        while path_exists:
            i = i + 1
            backup_path = u'%s_quarantine_%d%s' % (name, i, extension)
            path_exists = os.path.exists(backup_path)
        return backup_path

    def replace(self, new_file, lastfm_fingerprint_id=None):
        if not os.path.exists(new_file):
            logger.info('new_file %s does not exist' % (new_file))
            return

        logger.debug('file of %d is being replaced' % (self.id))
        song_path = self.get_song_path()
        path = os.path.dirname(song_path)

        if self.file_exists():
            backup_path = self.find_backup_path()
            shutil.copy(song_path, backup_path)
            logger.debug('original file saved at %s' % (backup_path))

        if not os.path.exists(path):
            logger.debug('creating path %s' % (path))
            os.makedirs(path)
        shutil.copy(new_file, song_path)
        self.generate_low_quality()

        # update db attributes
        if lastfm_fingerprint_id is not None:
            self.lastfm_fingerprint_id = lastfm_fingerprint_id
        self.filesize = os.path.getsize(song_path)
        self.save()
        logger.debug('replacement of %s done' % (self.id))

    def get_filepath_for_preview(self):
        song_path = self.get_song_path()
        name, extension = os.path.splitext(song_path)
        preview = u'%s_preview64%s' % (name, extension)
        return preview

    def get_filepath_for_lq(self):
        song_path = self.get_song_path()
        name, extension = os.path.splitext(song_path)
        preview = u'%s_lq%s' % (name, extension)
        return preview

    def generate_preview(self):
        import subprocess as sub
        source = self.get_song_path()
        destination = self.get_filepath_for_preview()

        logger.debug('generating preview for %s' % (source))
        args = [settings.FFMPEG_BIN,
                '-i',
                source]
        args.extend(settings.FFMPEG_GENERATE_PREVIEW_OPTIONS.split(" "))
        args.append(destination)
        p = sub.Popen(args, stdout=sub.PIPE, stderr=sub.PIPE)
        _output, errors = p.communicate()
        if len(errors) == 0:
            logger.error('error while generating preview of %d' % (self.id))
            logger.error(errors)

    def generate_low_quality(self):
        import subprocess as sub
        source = self.get_song_path()

        directory = mkdtemp(dir=settings.TEMP_DIRECTORY)
        destination = u'%s/converted.mp3' % (directory)
        logger.debug('generating lq for %s' % (source))
        args = [settings.FFMPEG_BIN,
                '-i',
                source]
        args.extend(settings.FFMPEG_CONVERT_LOW_QUALITY_OPTIONS.split(" "))
        args.append(destination)
        p = sub.Popen(args, stdout=sub.PIPE, stderr=sub.PIPE)
        _output, errors = p.communicate()
        if len(errors) == 0:
            logger.error('error while generating lq of %d' % (self.id))
            logger.error(errors)

        lq_destination = self.get_song_lq_path()
        try:
            shutil.copy(destination, lq_destination)
        except:
            logger.error('cannot copy %s to %s' % (destination, lq_destination))
        shutil.rmtree(directory)

    def file_exists(self):
        path = self.get_song_path()
        return os.path.exists(path)

    def lq_file_exists(self):
        """ check if low quality file exists """
        path = self.get_song_lq_path()
        return os.path.exists(path)

    class Meta:
        db_table = u'yasound_song'
        db_name = u'yasound'

    def __unicode__(self):
        return self.name


class YasoundSongGenre(models.Model):
    song = models.ForeignKey(YasoundSong)
    genre = models.ForeignKey(YasoundGenre)

    class Meta:
        db_table = u'yasound_song_genre'
        db_name = u'yasound'
        unique_together = ('song', 'genre')

    def __unicode__(self):
        return self.genre.name
