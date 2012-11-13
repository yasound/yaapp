from django.conf import settings
from xml.dom import minidom
import urllib
import re
import logging
logger = logging.getLogger("yaapp.yabase")

import pygeoip

HTTP_PROXY = None


def getProxy(http_proxy=None):
    """get HTTP proxy"""
    return http_proxy or HTTP_PROXY


def getProxies(http_proxy=None):
    http_proxy = getProxy(http_proxy)
    if http_proxy:
        proxies = {"http": http_proxy}
    else:
        proxies = None
    return proxies


class Bag:
    pass

_intFields = ('totalResultsCount')
_dateFields = ()
_listFields = ('code', 'geoname', 'country',)
_floatFields = ('lat', 'lng', 'distance')


def unmarshal(element):
    #import pdb;pdb.set_trace()
    rc = Bag()
    childElements = [e for e in element.childNodes if isinstance(e, minidom.Element)]
    if childElements:
        for child in childElements:
            key = child.tagName
            if hasattr(rc, key):
                if key in _listFields:
                    setattr(rc, key, getattr(rc, key) + [unmarshal(child)])
            elif isinstance(child, minidom.Element) and (child.tagName in ()):
                rc = unmarshal(child)
            elif key in _listFields:
                setattr(rc, key, [unmarshal(child)])
            else:
                setattr(rc, key, unmarshal(child))
    else:
        rc = "".join([e.data for e in element.childNodes if isinstance(e, minidom.Text)])
        if str(element.tagName) in _intFields:
            rc = int(rc)
        elif str(element.tagName) in _floatFields:
            rc = float(rc)
        elif str(element.tagName) in _dateFields:
            year, month, day, hour, minute, second = re.search(r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})', rc).groups()
            rc = (int(year), int(month), int(day), int(hour), int(minute), int(second), 0, 0, 0)
    return rc


def _do(url, http_proxy):
    proxies = getProxies(http_proxy)
    u = urllib.FancyURLopener(proxies)
    usock = u.open(url)
    rawdata = usock.read()
    xmldoc = minidom.parseString(rawdata)
    usock.close()
    data = unmarshal(xmldoc)
    if 0:
        return None
    else:
        return data


def _buildextendedFindNearby(lat, lng):
    searchUrl = "http://ws.geonames.org/extendedFindNearby?lat=%(lat)s&lng=%(lng)s" % vars()
    return searchUrl


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


def extendedFindNearby(lat, lng, http_proxy=None):
    """

    """
    url = _buildextendedFindNearby(lat, lng)
    return _do(url, http_proxy).geonames
