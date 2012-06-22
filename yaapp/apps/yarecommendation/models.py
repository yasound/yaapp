from django.conf import settings
from django.db.models import signals
from pymongo import DESCENDING
from yabase.models import SongMetadata, Radio
from yarecommendation.task import async_add_radio
from yarecommendation.utils import top_matches
from yaref.models import YasoundSong, YasoundGenre
from yasearch.utils import get_simplified_name
import logging
logger = logging.getLogger("yaapp.yarecommendation")


class ClassifiedRadiosManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.recommendation.radios
        self.collection.ensure_index("db_id")
    
    def drop(self):
        self.collection.drop()
    
    def add_radio(self, radio):
        artists = SongMetadata.objects.filter(songinstance__playlist__radio=radio).exclude(artist_name='').values_list('artist_name', flat=True)
        classification = {}
        has_data = False
        for artist in artists:
            has_data = True
            artist_name = get_simplified_name(artist).replace('.', '').replace('$', '')
            classification[artist_name] = classification.get(artist_name, 0) + 1

        if has_data:
            doc = {
                'db_id' : radio.id,
                'classification': classification
            }
            self.collection.update({'db_id': radio.id}, {'$set': doc}, upsert=True, safe=True)
    
    def populate(self):
        radios = Radio.objects.filter(ready=True)
        count = radios.count()
        logger.info('%d radios to compute' % (count))
        self.drop()
        for i, radio in enumerate(radios):
            if i % 1000 == 0:
                logger.info('computed %d radios (%d%%)', i+1, 100*(i+1)/count)
            self.add_radio(radio)
        logger.info('computed %d radios (%d%%)', i+1, 100*(i+1)/count)
        logger.info('done')
            
    def calculate_similar_radios(self):
        docs = list(self.all())
        count = len(docs)
        logger.info('%d radios to compute' % (count))
        for i,doc in enumerate(docs):
            if i % 1000 == 0:
                logger.info('computed %d radios (%d%%)', i+1, 100*(i+1)/count)
            scores = top_matches(docs, doc, 10)
            self.collection.update({'db_id': doc.get('db_id')}, 
                                   {'$set': {
                                        'similar_radios': scores
                                    }}, 
                                   upsert=True, 
                                   safe=True)
        logger.info('computed %d radios (%d%%)', i+1, 100*(i+1)/count)
        logger.info('done')
        
    def all(self):
        return self.collection.find()
    
    def radio_doc(self, radio_id):
        return self.collection.find_one({'db_id': radio_id})
    
def new_radio(sender, instance, created, **kwargs):
    if created:
        async_add_radio.apply_async(args=[instance], countdown=60*60)

def install_handlers():
    signals.post_save.connect(new_radio, sender=Radio)
install_handlers()    
    