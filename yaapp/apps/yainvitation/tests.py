from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from yabase.models import Radio
from models import Invitation
from account import settings as account_settings

class TestModels(TestCase):
    def setUp(self):
        user = User(email="test@yasound.com", username="test", is_superuser=False, is_staff=False)
        user.set_password('test')
        user.save()
        self.client.login(username="test", password="test")
        self.user = user        
    
        
    def test_accept(self):
        # build some data
        radio = Radio(creator=None, name='radio1')
        radio.save()
        
        invitation = Invitation(fullname='fullname',
                                user=self.user,
                                email='test@yasound.com',
                                invitation_key='key',
                                radio=radio)
        invitation.save()
        self.assertEqual(radio.creator, None)
        invitation.accept(self.user)
        self.assertEqual(radio.creator, self.user)
        
        groups = self.user.groups.all()
        self.assertEqual(len(groups), 1)
        group = groups[0]
        self.assertEquals(group.name, account_settings.GROUP_NAME_VIP)
        