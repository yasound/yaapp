from django.core.management.base import BaseCommand
from optparse import make_option
from yabase import task
from yabase.models import Playlist, Radio, SongMetadata
from yaref.models import YasoundSong
from yacore.database import queryset_iterator
import logging

from yabase.models import Radio
logger = logging.getLogger("yaapp.yabase")

class Command(BaseCommand):
    """
    Generate mp3 preview
    """
    option_list = BaseCommand.option_list + (
        make_option('-D', '--delete', dest='delete_radios', action='store_true',
            default=0, help="delete all fake radios"),
        make_option('-m', '--max', dest='radio_count',
            default=50, help="number of radios (default=50)"),
    )
    help = "Generate fake radios"
    args = ''

    def handle(self, *app_labels, **options):
        import codecs
        radios = Radio.objects.all()
        f = codecs.open('/tmp/tags.py', "w", "utf-8")
        for radio in radios:
            tags = radio.tags.all()
            cleaned_tags = []
            for tag in tags:
                cleaned_tag = tag.name.strip().lower()
                if len(cleaned_tag) > 0:
                    cleaned_tags.append(cleaned_tag)
            cleaned_tags = list(set(cleaned_tags))
            
            tags_string = ''
            for tag in cleaned_tags:
                tags_string = tags_string + ',' + 'u"' + tag + '"'
            
            if len(tags_string) > 0 and tags_string[0] == ',':
                tags_string = tags_string[1:]
            else:
                continue
            
            line = 'Radio.objects.get(id=%d).tags.add(%s)' % (radio.id, tags_string)
            f.write(line + '\n')
            line = 'logger.info("radio id = %d")' % (radio.id)
            f.write(line + '\n')

        f.close()            
        logger.info("done")
        
        
