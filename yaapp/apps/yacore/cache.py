from django.core.cache import cache as memcached
import cPickle as pickle

CACHE_EXPIRATION = 1 * 60 * 60


def cached_object(key):
    obj = memcached.get(key)
    if obj is None:
        return None
    return pickle.loads(obj)


def cache_object(key, obj):
    if obj is None:
        invalidate_object(key)
        return

    memcached.set(key, pickle.dumps(obj), CACHE_EXPIRATION)


def invalidate_object(key):
    memcached.delete(key)
