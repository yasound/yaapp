from django.http import HttpResponseRedirect
import logging
logger = logging.getLogger("yaapp.yabase")

class DoubleSlashMiddleware(object):
    """
    Handle the bug of iOS 4 clients sending 2 // instead of one
    """
    def process_response(self, request, response):
        if response.status_code == 404:
            url = request.path
            if url and '//' in url:
                url = url.replace("//", "/")
                return HttpResponseRedirect(url)
        return response

