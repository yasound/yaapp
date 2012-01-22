# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from optparse import make_option
from time import time
from yabase import metaphone
from yabase.models import YasoundArtist, YasoundAlbum, YasoundSong,\
    YasoundDoubleMetaphone
import datetime




class Command(BaseCommand):
    """
    Update action states
    """
    option_list = BaseCommand.option_list + (
        make_option('-D', '--dry-run', dest='dry', action='store_true',
            default=False, help="Dry run : don't update', only simulation"),
    )
    help = "Generate fuzzy index"
    args = ''

    def dm_from_sentence(self, sentence):
        dms = []
        words = sorted(sentence.lower().split())
        for word in words:
            dm = metaphone.dm(word)
            dm_record, created = YasoundDoubleMetaphone.objects.get_or_create(primary=dm[0],
                                                                              secondary=dm[1])
            dms.append(dm_record)
        return dms


    def handle(self, *app_labels, **options):
        dry = options.get('dry',False)
        
        artists = YasoundArtist.objects.all()
        for artist in artists:
            dms = self.dm_from_sentence(artist.name)
            artist.dms.clear()
            for dm in dms:
                print "adding %s" % (dm) 
                artist.dms.add(dm)
#        albums = YasoundAlbum.objects.all()
#        for album in albums:
#            dms = self.dm_from_sentence(album.name)
#            for dm in dms:
#                album.dms.add(dm)
#        
#        songs = YasoundSong.objects.all()
#        for song in songs:
#            dms = self.dm_from_sentence(song.name)
#            for dm in dms:
#                song.dms.add(dm)
        
        
        print "ok"
        