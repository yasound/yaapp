from django.test import TestCase
from models import Continent, Country, Genre, Radio
from import_utils import import_continent, import_country, import_genre, import_radio, import_radio_genre

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

    def test_import_genre(self):
        path = './apps/radioways/fixtures/YasoundGenre.txt'
        self.assertEquals(Genre.objects.all().count(), 0)

        import_genre(path)
        self.assertEquals(Genre.objects.all().count(), 91)

    def test_import_radio(self):
        import_continent('./apps/radioways/fixtures/r_continent.txt')
        import_country('./apps/radioways/fixtures/YasoundCountry.txt')
        import_genre('./apps/radioways/fixtures/YasoundGenre.txt')

        self.assertEquals(Radio.objects.all().count(), 0)
        import_radio('./apps/radioways/fixtures/YasoundRadio.txt')
        self.assertEquals(Radio.objects.all().count(), 913)

        import_radio_genre('./apps/radioways/fixtures/YasoundRadioGenre.txt')
