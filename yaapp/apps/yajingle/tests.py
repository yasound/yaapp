from django.test import TestCase
from models import JingleManager
from django.contrib.auth.models import User
from yabase.models import Radio
from models import Jingle


class JingleManagerTest(TestCase):
    def setUp(self):
        self.manager = JingleManager()
        self.manager.collection.drop()

    def test_creation(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()

        radio = Radio(creator=user)
        radio.save()

        jingle = self.manager.create_jingle(name='jingle', description='description', radio=radio, creator=user, filename='toto', duration=0)
        self.assertIsNotNone(jingle)
        jingles = self.manager.jingles_for_radio(radio.uuid)
        self.assertEquals(jingles.count(), 1)

        self.assertEquals(Jingle.objects.all().count(), 1)
