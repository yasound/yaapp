from django.test import TestCase
from django.contrib.auth.models import User
from models import TransientRadioHistoryManager
from yabase.models import Radio, Playlist

class ShowTest(TestCase):
    def setUp(self):
        self.manager = TransientRadioHistoryManager()
        self.manager.erase_informations()

        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.user = user

    def test_radio_created(self):
        self.assertEquals(self.manager.events_for_radio(None).count(), 0)

        radio = Radio.objects.create(uuid='uuid', creator=self.user)
        radio.ready=True
        radio.save()

        self.assertEquals(self.manager.events_for_radio(radio.uuid).count(), 1)

        Playlist.objects.create(name='playlist2', radio=radio)
        Playlist.objects.get(name='playlist2').delete()
        self.assertEquals(self.manager.events_for_radio(radio.uuid).count(), 2)
