from django.core.urlresolvers import resolve
import logging
from django.db import connection
from django.http import HttpResponse

import time
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


class SqlProfilingMiddleware(object):
    Queries = []

    def process_request(self, request):
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        return None

    def process_template_response(self, request, response):
        self._add_sql_queries(request)
        return response

    def process_response(self, request, response):
        if len(SqlProfilingMiddleware.Queries) > 1500:
            SqlProfilingMiddleware.Queries = SqlProfilingMiddleware.Queries[:1500]
        self._add_sql_queries(request)
        return response

    def process_exception(self, request, exception):
        return None

    def _add_sql_queries(self, request):
        if not 'api' in request.path:
            return
        for q in connection.queries:
            q["time"] = time.time() + float(q["time"])
            SqlProfilingMiddleware.Queries.insert(0, q)
            # add request info as a separator
        SqlProfilingMiddleware.Queries.insert(0, {"time": time.time(), "path": request.path})


class AllowOriginMiddleware(object):
    def process_request(self, request):
        if request.method == 'OPTIONS':
            return HttpResponse()

    def process_response(self, request, response):
        origin = request.META.get('HTTP_ORIGIN')
        if origin and origin == 'http://yasound.com/deezer/':
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, DELETE, PUT'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
