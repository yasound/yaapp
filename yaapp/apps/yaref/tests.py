from django.test import TestCase
from yaref.utils import get_simplified_name

class TestUtils(TestCase):
    def setUp(self):
        pass
    
    def test_get_simplified_name(self):
        name = "Welcome, cruel world (hi)"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, "welcome cruel world hi")

        name = "Alan's Psychedelic Breakfast"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, "alan s psychedelic breakfast")
           
        name = "Another Brick in the Wall, Pt. 3"
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, "another brick in the wall pt 3")

        name = "Is there anybody?.."
        simplified_name = get_simplified_name(name)
        self.assertEquals(simplified_name, "is there anybody")
