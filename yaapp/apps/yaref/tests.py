# -*- coding: utf-8 -*-
from django.test import TestCase
from yaref.models import YasoundSong
from yasearch.utils import get_simplified_name
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
    
    def test_find_mbid(self):
        s = YasoundSong(name='Believe', artist_name='Cher', lastfm_id='1019817')
        mbid = s.find_mbid()
        self.assertEquals(mbid, '028523f5-23b3-4910-adc1-46d932e2fb55')

    def test_find_synonyms(self):
        s = YasoundSong(name='hi', artist_name='world', lastfm_id='1019817', musicbrainz_id='028523f5-23b3-4910-adc1-46d932e2fb55')
        synonyms = s.find_synonyms()
        self.assertEquals(len(synonyms), 2)
        metadata = synonyms[0]
        self.assertEquals(metadata.get('name'), 'Believe')
        self.assertEquals(metadata.get('artist'), 'Cher')
        self.assertEquals(metadata.get('album'), 'Believe')
        