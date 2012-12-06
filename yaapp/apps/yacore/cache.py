from django.core.cache import cache as memcached
import cPickle as pickle

CACHE_EXPIRATION = 1 * 60 * 60


def cached_object(key, default_if_None=None):
    obj = memcached.get(key)
    if obj is None:
        return default_if_None
    return pickle.loads(obj)


def cache_object(key, obj, ttl=None):
    if obj is None:
        invalidate_object(key)
        return
    if ttl is None:
        ttl = CACHE_EXPIRATION
    memcached.set(key, pickle.dumps(obj), ttl)


def invalidate_object(key):
    memcached.delete(key)
