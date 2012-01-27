# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from optparse import make_option
from time import time
from yaref.models import YasoundArtist, YasoundAlbum, YasoundSong, \
    YasoundDoubleMetaphone
import datetime
import gc



def queryset_iterator(queryset, chunksize=1000):
    '''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    '''
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()

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

    def handle(self, *app_labels, **options):
        dry = options.get('dry',False)
        
        songs = YasoundSong.objects.all()
        last_indexed = YasoundSong.objects.last_indexed()
        if last_indexed:
            print "last indexed = %d" % (last_indexed.id)
            songs = songs.filter(id__gt=last_indexed.id)
        count = songs.count()
        print "processing %d songs" % (count)
        from time import time
        if count > 0:
            start = time()
            for i, song in enumerate(queryset_iterator(songs)):
                song.build_fuzzy_index()
                if i % 1000 == 0:
                    print "processed %d/%d (%d/100)" % (i, count, 100*i/count)
                    elapsed = time() - start
                    print 'elapsed time ' + str(elapsed) + ' seconds'
                    start = time()
                    
        print "done"
        
