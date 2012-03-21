from django.core.urlresolvers import resolve
import logging
logger = logging.getLogger("yaapp.yabase")

class DoubleSlashMiddleware(object):
    """
    Handle the bug of iOS 4 clients sending 2 // instead of one
    """
    def process_response(self, request, response):
        url = request.path
        if url and '//' in url:
            url = url.replace("//", "/")
            resolver_match = resolve(url)
            res = resolver_match.func(request, *resolver_match.args, **resolver_match.kwargs)
            return res
        return response
