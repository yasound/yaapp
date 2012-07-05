from bson.code import Code
from django.conf import settings
from django.db.models import signals
from pymongo import DESCENDING
from yabase.models import SongMetadata, Radio
from yarecommendation.task import async_add_radio
from yarecommendation.utils import top_matches, sim_pearson
from yaref.models import YasoundSong, YasoundGenre
from yasearch.utils import get_simplified_name
import logging
logger = logging.getLogger("yaapp.yarecommendation")


class MapArtistManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.recommendation.map_artist
        self.collection.ensure_index("code", unique=True)
        self.collection.ensure_index("artist", unique=True)
    def drop(self):
        self.collection.drop()

    def next_code(self):
        next_code = 0
        last_docs = self.collection.find().sort([('code', DESCENDING)]).limit(1)
        if last_docs.count() != 0:
            next_code = last_docs[0].get('code') + 1
        return  next_code

    def artist_code(self, artist_name):
        code = None
        doc = self.collection.find_one({'artist': artist_name})
        if doc is None:
            code = self.next_code()
            doc = {
                'code': code,
                'artist': artist_name
            }
            self.collection.insert(doc, safe=True)
        else:
            code = doc.get('code')
        return code

    def artist_name(self, code):
        doc = self.collection.find_one({'code': code})
        if doc:
            return doc.get('artist')
        return None
        

class ClassifiedRadiosManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.recommendation.radios
        self.collection.ensure_index("db_id", unique=True)
    def drop(self):
        self.collection.drop()
    
    def add_radio(self, radio):
        ma = MapArtistManager()
        artists = SongMetadata.objects.filter(songinstance__playlist__radio=radio).exclude(artist_name='').values_list('artist_name', flat=True)
        classification = {}
        artist_list = []
        for artist in artists:
            artist_name = get_simplified_name(artist).replace('.', '').replace('$', '')
            artist_code = ma.artist_code(artist_name)
            classification[str(artist_code)] = classification.get(str(artist_code), 0) + 1
            artist_list.append(artist_code)
        doc = {
            'db_id' : radio.id,
            'classification': classification,
            'artists': list(set(artist_list))
        }
        self.collection.update({'db_id': radio.id}, {'$set': doc}, upsert=True, safe=True)
           
    
    def populate(self):
        radios = Radio.objects.filter(ready=True)
        count = radios.count()
        logger.info('%d radios to compute' % (count))
        for i, radio in enumerate(radios):
            if i % 100 == 0:
                logger.info('computed %d radios (%d%%)', i+1, 100*(i+1)/count)
            self.add_radio(radio)
        logger.info('computed %d radios (%d%%)', i+1, 100*(i+1)/count)
        logger.info('done')
            
    def calculate_similar_radios(self):
        docs = list(self.all())
        count = len(docs)
        logger.info('%d radios to compute' % (count))
        for i,doc in enumerate(docs):
            if i % 100 == 0:
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
        
        
    def _intersect(self, a, b):
        return list(set(a) & set(b))
        
    def _co_occurrences(self, a, b):
        return float(len(self._intersect(a, b)))
    
    def find_similar_radios(self, artists):
        ma = MapArtistManager()
        similarities = []
        if len(artists) == 0:
            return similarities
        artists_sanitized = []
        for artist in artists:
            artist_name = get_simplified_name(artist).replace('.', '').replace('$', '')
            artists_sanitized.append(ma.artist_code(artist_name))
        
        docs = self.collection.find()
        for doc in docs:
            doc_artists = doc.get('artists')
            if len(doc_artists) == 0:
                continue
            
            similarity = 0.5 * (self._co_occurrences(artists_sanitized, doc_artists) / 
                                self._co_occurrences(artists_sanitized, artists_sanitized) + 
                                self._co_occurrences(doc_artists, artists_sanitized) / 
                                self._co_occurrences(doc_artists, doc_artists))

            if similarity > 0:
                similarities.append((similarity, doc.get('db_id')))
        similarities.sort()
        similarities.reverse()
        similarities = similarities[0:20]
        return similarities 

        
        
    def all(self):
        return self.collection.find()
    
    def radio_doc(self, radio_id):
        return self.collection.find_one({'db_id': radio_id})
    
class RadiosClusterManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.recommendation.cluster
        self.collection.ensure_index("db_id", unique=False)
        self.collection.ensure_index("root", unique=False)
    def drop(self):
        self.collection.drop()
        
        
    def _pprint(self, node, depth):
        if node is None:
            return
        print "-" * depth, "", node.get('_id'), "virtual:", node.get('virtual')
        self._pprint(self._get_left_child(node), depth+2)
        self._pprint(self._get_right_child(node), depth+2)
        
    def pprint(self):
        root = self._root_node()
        depth=1
        print "-" * depth, "", root.get('_id'), "(root)"
        self._pprint(self._get_left_child(root), depth=depth+2)
        self._pprint(self._get_right_child(root), depth=depth+2)
        
    def _root_node(self):
        root = self.collection.find_one({'root': True})
        if not root:
            self._create_root()
            root = self.collection.find_one({'root': True})
        return root
    
    def _get_left_child(self, parent):
        return self.collection.find_one({'_id': parent.get('left')})
        
    def _get_right_child(self, parent):
        return self.collection.find_one({'_id': parent.get('right')})

    def _find_in_nodes(self, parent, radio, current_score=0, stop_score=None):
        print "current_score = %f, stop_score=%s" %(current_score, stop_score)
        if stop_score is not None and stop_score <= current_score:
            print "stop_score reached: (stop_score) %f < %f (current_score) " % (stop_score, current_score)
            return parent
        
        left_child = self._get_left_child(parent)
        right_child = self._get_right_child(parent)
        
        left_score, right_score = 0, 0
        if left_child:
            left_score = abs(sim_pearson(left_child, radio))
        if right_child:
            right_score = abs(sim_pearson(right_child, radio))
        
        if current_score > left_score and current_score > right_score:
            return parent
        
        if left_score >= right_score:
            if left_child is None:
                return parent
            return self._find_in_nodes(left_child, radio, left_score, stop_score=stop_score)
        else:
            if right_child is None:
                return parent
            return self._find_in_nodes(right_child, radio, right_score, stop_score=stop_score)
            
    def _find_node(self, radio, stop_score):
        root = self._root_node()
        return self._find_in_nodes(root, radio, current_score=0, stop_score=stop_score)
        
    def _create_root(self):
        doc = {
            'parent': None,
            'root': True,
            'virtual': True,
            'left': None,
            'right': None,
            'db_id': None,
            'classification': None
        }
        self.collection.insert(doc, safe=True)
    
    def _add_new_radio(self, parent, radio):
        doc = {
            'parent': None,
            'root': False,
            'virtual': False,
            'left': None,
            'right': None,
            'db_id': radio.get('db_id'),
            'classification': radio.get('classification')
        }
        self.collection.save(doc, safe=True)
        if parent is None:
            return doc
    
        doc['parent'] = parent.get('_id')
        if parent.get('left') == None:
            parent['left'] = doc.get('_id')
        else:
            parent['right'] = doc.get('_id')

        self.collection.save(doc, safe=True)
        self.collection.save(parent, safe=True)
        return doc
    
    def _is_leaf(self, node):
        left = node.get('left')
        right = node.get('right')
        if left is None and right is None:
            return True
        return False
    
    def _generate_virtual_node(self, node1, radio):
        node2 = self._add_new_radio(None, radio)
        
        classification1 = node1.get('classification')
        classification2 = node2.get('classification')
        
        keys1 = classification1.keys()
        keys2 = classification2.keys()
        
        merged_classification = {}
        
        for artist in keys1:
            if artist in keys2:
                val1 = classification1[artist]
                val2 = classification2[artist]
                mean = float( (val1 + val2) / 2)
                merged_classification[artist] = mean
                del classification2[artist]
                del classification1[artist]
            else:
                merged_classification[artist] = classification1[artist]

        keys1 = classification1.keys()
        keys2 = classification2.keys()
        for artist in keys2:
            if artist in keys1:
                val1 = classification1[artist]
                val2 = classification2[artist]
                mean = float( (val1 + val2) / 2)
                merged_classification[artist] = mean
            else:
                merged_classification[artist] = classification2[artist]
        
        doc = {
            'parent': None,
            'root': False,
            'virtual': True,
            'db_id': None,
            'left': node1.get('_id'),
            'right': node2.get('_id'),
            'classification': merged_classification
        }
        self.collection.save(doc, safe=True)
        
        node2['parent'] = doc.get('_id')
        self.collection.save(node2, safe=True)
        
        return doc

    def _parent_node(self, node):
        if node.get('root') == True:
            return node
        return self.collection.find_one({'_id': node.get('parent')})
    
    def _replace_child(self, parent, node1, node2):
        if parent.get('left') == node1.get('_id'):
            parent['left'] = node2.get('_id')
        else:
            parent['right'] = node2.get('_id')
            
        node2['parent'] = node1.get('parent')
        node1['parent'] = node2.get('_id')
        self.collection.save(node2, safe=True)
        self.collection.save(node1, safe=True)
        self.collection.save(parent, safe=True)
    
    def add_radio(self, radio):
        nearest_node = self._find_node(radio)
        if nearest_node.get('root') == True:
            self._add_new_radio(self._root_node(), radio)
        else:
            virtual_node = self._generate_virtual_node(nearest_node, radio)
            parent_node = self._parent_node(nearest_node)
            self._replace_child(parent_node, nearest_node, virtual_node)
    
    def _radios_from_node(self, node, radio):
        res = []
        if node.get('db_id'):
            score = abs(sim_pearson(node, radio))
            if score >= 0.9:
                res.append(node.get('db_id'))
                
        left = self._get_left_child(node)
        if left:
            res.extend(self._radios_from_node(left, radio))
        right = self._get_right_child(node)
        if right:
            res.extend(self._radios_from_node(right, radio))
        return res
        
    def find_radios(self, artists):
        res = []
        fake_radio = {
            'classification': artists
        }
        node = self._find_node(fake_radio, stop_score=0.9)
        print node
        if node is None:
            return res
        else:
            res = self._radios_from_node(node, fake_radio)
        return res
    
def new_radio(sender, instance, created, **kwargs):
    if created:
        async_add_radio.apply_async(args=[instance], countdown=60*60)

def install_handlers():
    signals.post_save.connect(new_radio, sender=Radio)
install_handlers()    
    