# -*- coding: utf-8 -*-
from django.test import TestCase
from yaref.models import YasoundSong
from yaref.mongo import SongAdditionalInfosManager
from yasearch.utils import get_simplified_name, build_dms
from yasearch import settings as yasearch_settings
from yasearch.models import build_mongodb_index

import test_utils as yaref_test_utils
import buylink

class TestUtils(TestCase):
    def setUp(self):
        pass

    def test_get_simplified_name(self):
        name = u"スマイライフ"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"sumairaihu")

        name = u"誰是MVP"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"shui shi mvp")

        name = "Welcome, cruel world (hi)"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"welcome cruel world hi")

        name = "Alan's Psychedelic Breakfast"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"alan s psychedelic breakfast")

        name = "Another Brick in the Wall, Pt. 3"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"another brick in the wall pt 3")

        name = "Is there anybody?.."
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"is there anybody")

        name = "Some %^(({}))'\"?<>punctuation-+*&`~:"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"some punctuation")

        name = u"Julien Doré est français"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"julien dore est francais")

        name = "Julien Doré"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"julien dore")

        name = u"Москва"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"moskva")

        name = u"שיפל"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"shypl")

        name = u"طبيب"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"tbyb")

        name = u"Français"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"francais")

        name = None
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, None)

    def test_build_dms(self):
        query = 'Les plus belles chansons françaises'
        dms = build_dms(query, True, yasearch_settings.SONG_STRING_EXCEPTIONS)
        self.assertEquals(dms, ['XNSN', 'FRNS', 'PLS'])

        query = u'Les plus belles chansons françaises'
        dms = build_dms(query, True, yasearch_settings.SONG_STRING_EXCEPTIONS)
        self.assertEquals(dms, ['XNSN', 'FRNS', 'PLS'])

        query = 'Les plus belles chansons francaises'
        dms = build_dms(query, True, yasearch_settings.SONG_STRING_EXCEPTIONS)
        self.assertEquals(dms, ['XNSN', 'FRNK', 'PLS'])


        query = 'Portela h\xc3\xa9'
        dms = build_dms(query, True, yasearch_settings.SONG_STRING_EXCEPTIONS)
        self.assertEquals(dms, ['PRTL'])

class TestBuyLink(TestCase):
    def setUp(self):
        pass

    def test_generate_buy_link_ok(self):
        name = 'gatekeeper'
        artist = 'feist'
        album = 'let it die'

        url = buylink.generate_buy_link(name, album, artist)
        self.assertIsNotNone(url)

    def test_generate_buy_link_with_wrong_album(self):
        name = 'gatekeeper'
        artist = 'feist'
        album = 'wrong album'

        url = buylink.generate_buy_link(name, album, artist)
        self.assertIsNotNone(url)

    def test_generate_buy_link_with_no_results(self):
        name = 'sdpsdlsds'
        artist = 'sdsdsd'
        album = 'sdsdsdds'

        url = buylink.generate_buy_link(name, album, artist)
        self.assertIsNone(url)

class TestFind(TestCase):
    def setUp(self):
        pass

# disabled because response from echonest is not consistent
    # def test_find_mbid(self):
    #     s = YasoundSong(name='Believe', artist_name='Cher', lastfm_id='1019817')
    #     mbid = s.find_mbid()
    #     self.assertEquals(mbid, '028523f5-23b3-4910-adc1-46d932e2fb55')

    # def test_find_synonyms(self):
    #     s = YasoundSong(name='hi', artist_name='world', lastfm_id='1019817', musicbrainz_id='028523f5-23b3-4910-adc1-46d932e2fb55')
    #     synonyms = s.find_synonyms()
    #     self.assertEquals(len(synonyms), 2)

#        metadata = synonyms[0]
#        self.assertEquals(metadata.get('name'), 'Believe')
#        self.assertEquals(metadata.get('artist'), 'Cher')
#        self.assertEquals(metadata.get('album'), 'Believe')

class TestAdditionalInfo(TestCase):
    def setUp(self):
        sa = SongAdditionalInfosManager()
        sa.erase_informations()

    def test_additional_info(self):
        info = {
            'conversion_status' : {
                'preview_generated': False,
                'hq_generated': False,
                'lq_generated': False
            },
            'verified': True
        }

        sa = SongAdditionalInfosManager()
        sa.add_information(1, info)

        doc = sa.information(1)
        self.assertEquals(doc.get('conversion_status').get('preview_generated'), False)
        self.assertEquals(doc.get('verified'), True)

        sa.remove_information(1, 'conversion_status')
        doc = sa.information(1)
        self.assertIsNone(doc.get('conversion_status'))
        self.assertEquals(doc.get('verified'), True)

class TestFuzzy(TestCase):
    def setUp(self):
        pass

    def test_karaoke(self):
        bad_cure = yaref_test_utils.generate_yasound_song(name='from the edge of the deep green sea',
            artist='tribute to the cure',
            album='wish')

        good_cure = yaref_test_utils.generate_yasound_song(name='from the edge of the deep green sea',
            artist='the cure',
            album='wish')


        bad_queen = yaref_test_utils.generate_yasound_song(name='innuendo',
            artist='queen',
            album='karaoke version')

        good_queen = yaref_test_utils.generate_yasound_song(name='innuendo',
            artist='queen',
            album='good version')

        good_pixies = yaref_test_utils.generate_yasound_song(name='where is my mind',
            artist='pixies',
            album='live at houston (1992)')

        bad_pixies = yaref_test_utils.generate_yasound_song(name='where is my mind',
            artist='pixies',
            album='karaoke')

        bad_pixies2 = yaref_test_utils.generate_yasound_song(name='where is my mind',
            artist='tribute to the pixies',
            album='karaoke')

        build_mongodb_index(erase=True)

        res = YasoundSong.objects.find_fuzzy(name='where is my mind',
            artist='the pixies',
            album='')
        self.assertEquals(res.get('db_id'), good_pixies.id)


        res = YasoundSong.objects.find_fuzzy(name='from the edge of the deep green sea',
            artist='the cure',
            album='wish')
        self.assertEquals(res.get('db_id'), good_cure.id)

        res = YasoundSong.objects.find_fuzzy(name='innuendo',
            artist='queen',
            album='')
        self.assertEquals(res.get('db_id'), good_queen.id)

        res = YasoundSong.objects.find_fuzzy(name='innuendo',
            artist='queen',
            album='karaoke')
        self.assertEquals(res.get('db_id'), bad_queen.id)

        res = YasoundSong.objects.find_fuzzy(name='where is my mind',
            artist='',
            album='')
        self.assertEquals(res.get('db_id'), good_pixies.id)



        res = YasoundSong.objects.find_fuzzy(name='where is my mind',
            artist='',
            album='karaoke')
        self.assertEquals(res.get('db_id'), bad_pixies.id)

    def test_bad_matching(self):
        justice = yaref_test_utils.generate_yasound_song(name='Get It Together',
            artist='Justus League, Joe Scudda',
            album='Triple Play: The Second Inning')

        build_mongodb_index(erase=True)

        res = YasoundSong.objects.find_fuzzy(name="we've got to",
            artist='ayo',
            album='billie-eve')
        self.assertIsNone(res)

        ayo = yaref_test_utils.generate_yasound_song(name="we've got to",
            artist='ayo',
            album='billie-eve')
        build_mongodb_index(erase=True)

        res = YasoundSong.objects.find_fuzzy(name="we've got to",
            artist='ayo',
            album='billie-eve')
        print res
