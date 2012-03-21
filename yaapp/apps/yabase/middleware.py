from django.core.urlresolvers import resolve
from django.http import HttpResponseRedirect, HttpResponse
import logging
import urlparse
logger = logging.getLogger("yaapp.yabase")


from django.core.urlresolvers import RegexURLResolver, RegexURLPattern, Resolver404, get_resolver

__all__ = ('resolve_to_name',)

def _parse_match(match):
    args = list(match.groups())
    kwargs = match.groupdict()
    for val in kwargs.values():
        args.remove(val)
    return args, kwargs

def _pattern_resolve_to_name(self, path):
    match = self.regex.search(path)
    if match:
        name = ""
        if self.name:
            name = self.name
        elif hasattr(self, '_callback_str'):
            name = self._callback_str
        else:
            name = "%s.%s" % (self.callback.__module__, self.callback.func_name)
        args, kwargs = _parse_match(match)
        return name, args, kwargs

def _resolver_resolve_to_name(self, path):
    tried = []
    match = self.regex.search(path)
    if match:
        new_path = path[match.end():]
        for pattern in self.url_patterns:
            try:
                if isinstance(pattern,RegexURLPattern):
                    nak =  _pattern_resolve_to_name(pattern,new_path)
                else:
                    nak = _resolver_resolve_to_name(pattern,new_path)
            except Resolver404, e:
                tried.extend([(pattern.regex.pattern + '   ' + t) for t in e.args[0]['tried']])
            else:
                if nak:
                    return nak # name, args, kwargs
                tried.append(pattern.regex.pattern)
        raise Resolver404, {'tried': tried, 'path': new_path}


def resolve_to_name(path, urlconf=None):
    r = get_resolver(urlconf)
    if isinstance(r,RegexURLPattern):
        return _pattern_resolve_to_name(r,path)
    else:
        return _resolver_resolve_to_name(r,path)


class DoubleSlashMiddleware(object):
    """
    Handle the bug of iOS 4 clients sending 2 // instead of one
    """
    def process_response(self, request, response):
        if response.status_code == 404:
            url = request.path
            if url and '//' in url:
                url = url.replace("//", "/")
                if not url.endswith('/'):
                    url = url + '/'
                view, args, kwargs = resolve(url)
                if hasattr(view, 'view_func'):
                    view = view.view_func                
                kwargs['request'] = request
                res = view(*args, **kwargs)
                return HttpResponse(res)
        return response

