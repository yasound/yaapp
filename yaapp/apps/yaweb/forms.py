from bootstrap.forms import Fieldset, BootstrapForm
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

class BetatestForm(BootstrapForm):
    main_email = forms.CharField(label=_("Email"), max_length=255, required=True)
    lastname = forms.CharField(label=_("Last name"), required=True)
    firstname = forms.CharField(label=_("First name"), required=True)
    occupation = forms.CharField(label=_("Occupation"), required=True)
    age = forms.CharField(label=_("Age"), required=True)
    registered = forms.BooleanField(label=_("Are you registered at Yasound?"), required=False)
    facebook = forms.CharField(label=_("Facebook"), required=False)
    twitter = forms.CharField(label=_("Twitter"), required=False)
    email = forms.CharField(label=_("Email"), max_length=255, required=False)

    mac = forms.BooleanField(label=_("A mac"), required=False)
    mac_details = forms.CharField(label=_("Which one ?"), required=False)

    pc = forms.BooleanField(label=_("A PC"), required=False)
    pc_details = forms.CharField(label=_("Which one ?"), required=False)

    iphone = forms.BooleanField(label=_("An iPhone"), required=False)
    iphone_details = forms.CharField(label=_("Which one ?"), required=False)

    ipod = forms.BooleanField(label=_("An iPod"), required=False)
    ipod_details = forms.CharField(label=_("Which one ?"), required=False)

    ipad = forms.BooleanField(label=_("An iPad"), required=False)
    ipad_details = forms.CharField(label=_("Which one ?"), required=False)

    android = forms.BooleanField(label=_("A smartphone shipped with Android"), required=False)
    android_details = forms.CharField(label=_("Which one ?"), required=False)

    deezer = forms.BooleanField(label=_("Deezer"), required=False)
    spotify = forms.BooleanField(label=_("Spotify"), required=False)
    soundcloud = forms.BooleanField(label=_("Soundcloud"), required=False)
    grooveshark = forms.BooleanField(label=_("Grooveshark"), required=False)
    lastfm = forms.BooleanField(label=_("Lastfm"), required=False)
    radionomy = forms.BooleanField(label=_("Radionomy"), required=False)
    musicme = forms.BooleanField(label=_("MusicMe"), required=False)
    qobuz = forms.BooleanField(label=_("Qobuz"), required=False)
   
    deezer_paid = forms.BooleanField(label=_("Deezer"), required=False)
    spotify_paid = forms.BooleanField(label=_("Spotify"), required=False)
    soundcloud_paid = forms.BooleanField(label=_("Soundcloud"), required=False)
    grooveshark_paid = forms.BooleanField(label=_("Grooveshark"), required=False)
    lastfm_paid = forms.BooleanField(label=_("Lastfm"), required=False)
    radionomy_paid = forms.BooleanField(label=_("Radionomy"), required=False)
    musicme_paid = forms.BooleanField(label=_("MusicMe"), required=False)
    qobuz_paid = forms.BooleanField(label=_("Qobuz"), required=False)

    class Meta:
        layout = (
            Fieldset(_('General informations'),
                     'main_email',
                     'lastname',
                     'firstname',
                     'occupation',
                     'age'),
            Fieldset(_('You and Yasound'),
                     'registered',),
            Fieldset(_('What is your account ?'),
                     'facebook',
                     'twitter',
                     'email'),
            Fieldset(_('What equipment(s) do you have?'),
                     'mac',
                     'mac_details',
                     'pc',
                     'pc_details',
                     'iphone',
                     'iphone_details',
                     'ipod',
                     'ipod_details',
                     'ipad',
                     'ipad_details',
                     'android',
                     'android_details',),
            Fieldset(_('Are you registered at another music platform?'),
                     'deezer',
                     'spotify',
                     'soundcloud',
                     'grooveshark',
                     'lastfm',
                     'radionomy',
                     'musicme',
                     'qobuz',
                     ),
            Fieldset(_('Have you subscribed to paid options?'),
                     'deezer_paid',
                     'spotify_paid',
                     'soundcloud_paid',
                     'grooveshark_paid',
                     'lastfm_paid',
                     'musicme_paid',
                     'qobuz_paid',
                     ),
        )
        
        
    def clean(self):
        return self.cleaned_data
       
    
    def save(self):
        context = self.cleaned_data
        message = render_to_string("yaweb/betatest_mail_template.txt", context)
        subject = '[betatest] nouveau candidat'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [a[1] for a in settings.MODERATORS])
