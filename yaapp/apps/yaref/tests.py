# -*- coding: utf-8 -*-
from django.test import TestCase
from yaref.utils import get_simplified_name

class TestUtils(TestCase):
    def setUp(self):
        pass
    
    def test_get_simplified_name(self):
        name = u"スマイライフ"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"スマイライフ")

        name = u"誰是MVP"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"mvp")

        name = u"ÔÙπû‹¡Ê±ºò (‹Â¸è)(ÒôÏíÓéÂÛÌá’©"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"ouueoo a e ooiioeauia")
        
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

        name = u"Julien Doré"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"julien dore")

        name = "Julien Doré"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, u"julien dore")

        
        