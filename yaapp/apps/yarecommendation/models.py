from bson.code import Code
from django.conf import settings
from django.db.models import signals
from math import sqrt
from pymongo import DESCENDING, ASCENDING
from scipy.sparse import csc_matrix
from sklearn.neighbors import BallTree
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import MiniBatchKMeans
from time import time
from yabase.models import SongMetadata, Radio
from yarecommendation.task import async_add_radio
from yarecommendation.utils import top_matches, sim_pearson, tail_call_optimized
from yaref.models import YasoundSong, YasoundGenre
from yasearch.utils import get_simplified_name
import logging
import random
from scipy.io import mmread, mmwrite
import os
import numpy
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
        self.collection.ensure_index("cluster_id", unique=False)
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

    def find2(self, classification):
        rk = RadiosKMeansManager()
        cluster = rk.find_cluster(classification)
        
        
        
    def all(self):
        return self.collection.find()
    
    def radio_doc(self, radio_id):
        return self.collection.find_one({'db_id': radio_id})
    
class RadiosKMeansManager():
    def __init__(self):
        self.db = settings.MONGO_DB
        self.collection = self.db.recommendation.kmean
        self.collection.ensure_index("id", unique=True)
    
    def get_artist_count(self):
        ma = MapArtistManager()
        artist_count = ma.collection.find().count()
        return artist_count
    
    def create_matrix_line(self, artist_count, classification):
        line = [0]*artist_count
        for artist, count in classification.iteritems():
            line[int(artist)] = count
        return line
    
    def create_matrix(self, qs, id_key):
        """
        Create matrix from query set
        """
        logger.info('creating matrix data')
        start = time()
        items = []

        item_count = qs.count()
        data = []
        artist_count = self.get_artist_count()
        
        for item in qs:
            items.append(item.get(id_key))
            classification = item.get('classification')
            line = self.create_matrix_line(artist_count, classification);
            data.append(line)
        
        elapsed = time() - start
        logger.info('done in %s seconds, length is %dx%d' % (elapsed, item_count, artist_count))
            
        logger.info('transformation to sparse csc_matrix')
        start = time()
        matrix = csc_matrix(data)
        elapsed = time() - start
        logger.info('done in %s seconds' % elapsed)
        return items, matrix
    
    def get_radio_matrix_path(self):
        path = os.path.join(settings.RECOMMENDATION_CACHE, 'radio_matrix.mtx')
        return path

    def get_radio_index_path(self):
        path = os.path.join(settings.RECOMMENDATION_CACHE, 'radio_index.npy')
        return path
    
    def save_cache(self):
        logger.info('building cache')
        cm = ClassifiedRadiosManager()
        radios, matrix = self.create_matrix(cm.collection.find(), 'db_id')
        mmwrite(self.get_radio_matrix_path(), matrix)
        numpy.save(self.get_radio_index_path(), radios)

    def load_cache(self):
        matrix = mmread(self.get_radio_matrix_path())
        radios = numpy.load(self.get_radio_index_path())
        return radios, csc_matrix(matrix)
        
    
    def build_cluster(self, k=30):
        logger.info('building cluster, k=%d' % (k))
        cm = ClassifiedRadiosManager()
        radios, matrix = self.create_matrix(cm.collection.find(), 'db_id')
        self.collection.drop()
        
        logger.info('MiniBatchKMeans started')
        start = time()
        mbkm = MiniBatchKMeans(init="k-means++", k=k, max_iter=100, chunk_size=1000)
        mbkm.fit(matrix)
        elapsed = time() - start
        logger.info('done in %s seconds' % elapsed)
        
        logger.info('saving data to mongodb')
        start = time()
        # saving all data        
        for cluster_id, cluster in enumerate(mbkm.cluster_centers_):
            classification = {}
            for artist_id, artist_count in enumerate(cluster):
                classification[str(artist_id)] = artist_count 
            doc = {
                'id': cluster_id,
                'classification': classification
            }
            self.collection.insert(doc, safe=True)

        cm = ClassifiedRadiosManager()
        for radio_index, cluster_id in enumerate(mbkm.labels_):
            cm.collection.update({'db_id': radios[radio_index]}, 
                                 {'$set': {'cluster_id': int(cluster_id)}}, 
                                 safe=True)
        elapsed = time() - start
        logger.info('done in %s seconds' % elapsed)
        
        clusters = self.collection.find()
        for cluster in clusters:
            count = cm.collection.find({'cluster_id': cluster.get('id')}).count()
            logger.info('cluster %s : %d radios'  % (cluster.get('id'), count))

    def find_cluster(self, classification):
        # transform classification to sparse matrix
        artist_count = self.get_artist_count()
        line = self.create_matrix_line(artist_count, classification)
        clusters, matrix = self.create_matrix(self.collection.find(), 'id')
        
        neigh = NearestNeighbors(5)
        neigh.fit(matrix)
        _dist, ind = neigh.kneighbors(line)
        
        if len(ind) > 0:
            return [int(clusters[cluster_index]) for cluster_index in ind[0]]
        return []
    
    def find_radios(self, classification):
        clusters = self.find_cluster(classification)

        artist_count = self.get_artist_count()
        line = self.create_matrix_line(artist_count, classification)

        cm = ClassifiedRadiosManager()
        qs = cm.collection.find({'cluster_id': {'$in': clusters}})
        if qs.count() == 0:
            return None
        radios, matrix = self.create_matrix(qs, 'db_id')

        logger.info('calculating NearestNeighbors')        
        start = time()
        neigh = NearestNeighbors(10)
        neigh.fit(matrix)
        _dist, ind = neigh.kneighbors(line)
        elapsed = time() - start
        logger.info('done in %s seconds' % elapsed)

        if len(ind) > 0:
            return [radios[radio_index] for radio_index in ind[0]]
        return []
    
    def find_radios2(self, classification):
        artist_count = self.get_artist_count()
        line = self.create_matrix_line(artist_count, classification)
        radios, matrix = self.load_cache()
        
        logger.info('calculating NearestNeighbors')        
        start = time()
        neigh = NearestNeighbors(10)
        neigh.fit(matrix)
        _dist, ind = neigh.kneighbors(line)
        elapsed = time() - start
        logger.info('done in %s seconds' % elapsed)

        if len(ind) > 0:
            return [radios[radio_index] for radio_index in ind[0]]
        return []
        
    
def new_radio(sender, instance, created, **kwargs):
    if created:
        async_add_radio.apply_async(args=[instance], countdown=60*60)

def install_handlers():
    signals.post_save.connect(new_radio, sender=Radio)
install_handlers()    
    