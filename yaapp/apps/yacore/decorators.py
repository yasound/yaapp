from django.http import HttpResponseNotAllowed, HttpResponse
from django.utils.decorators import available_attrs
from django.utils.functional import wraps
from http import check_api_key_Authentication, coerce_put_post
import logging
logger = logging.getLogger("yaapp.yacore")

def check_api_key(methods=['GET', 'POST', 'PUT', 'DELETE'], login_required=True):
    """
    """
    def decorator(func):
        def inner(request, *args, **kwargs):
            if request.method not in methods:
                logger.warning('Method Not Allowed (%s): %s' % (request.method, request.path),
                    extra={
                        'status_code': 405,
                        'request': request
                    }
                )
                return HttpResponseNotAllowed(methods)
            
            coerce_put_post(request)                

            authorized = check_api_key_Authentication(request)
            
            if login_required:
                if not authorized:
                    authorized = request.user.is_authenticated()
                
                if not authorized:
                    return HttpResponse(status=401)
            
            return func(request, *args, **kwargs)
        return wraps(func, assigned=available_attrs(func))(inner)
    return decorator