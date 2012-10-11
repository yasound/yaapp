from django.test import TestCase
from models import Continent, Country
from import_utils import import_continent, import_country

class TestImport(TestCase):
    def setUp(self):
        pass

    def test_import_continent(self):
        path = './apps/radioways/fixtures/r_continent.txt'
        self.assertEquals(Continent.objects.all().count(), 0)

        import_continent(path)
        self.assertEquals(Continent.objects.all().count(), 7)

    def test_import_country(self):
        path = './apps/radioways/fixtures/r_continent.txt'
        self.assertEquals(Continent.objects.all().count(), 0)

        import_continent(path)
        self.assertEquals(Continent.objects.all().count(), 7)

        path = './apps/radioways/fixtures/YasoundCountry.txt'
        self.assertEquals(Country.objects.all().count(), 0)

        import_country(path)
        self.assertEquals(Country.objects.all().count(), 41)

