from django.conf import settings
import logging
logger = logging.getLogger("yaapp.yabase")

import pygeoip

def ip_city_record(ip):
    geo = pygeoip.GeoIP(settings.GEOIP_CITY_DATABASE)
    record = geo.record_by_addr(ip)
    return record

def ip_coords(ip):
    record = ip_city_record(ip)
    if record is None:
        return None
    return (record['latitude'], record['longitude'])

def ip_country(ip):
    geo = pygeoip.GeoIP(settings.GEOIP_DATABASE)
    return geo.country_code_by_addr(ip)

def request_city_record(request):
    return ip_city_record(request.META[settings.GEOIP_LOOKUP])

def request_coords(request):
    return ip_coords(request.META[settings.GEOIP_LOOKUP])

def request_country(request):
    return ip_country(request.META[settings.GEOIP_LOOKUP])



def can_login(request):
    if not (settings.PRODUCTION_MODE or settings.DEVELOPMENT_MODE):
        return True
    
    if request.user.is_superuser:
        return True

    c = request_country(request)
    if c in settings.GEOIP_AUTHORIZED_COUNTRIES:
        return True
    else:
        logger.info('login impossible for country "%s"' % (c))
    return False
    

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    

