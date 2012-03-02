# -*- coding: utf-8 -*-
from django.test import TestCase
from yasearch.utils import get_simplified_name

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
        