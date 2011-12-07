import os,sys

#raise RuntimeError('WSGI sends to the Apache2 error_log.')


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yaapp.settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.

#path = os.path.abspath(os.path.split(__file__)[0])
path = '/var/local/yaapp' #os.path.abspath(os.path.split(__file__)[0])
if path not in sys.path:
    sys.path.append(path)

path = '/var/local' #os.path.abspath(os.path.split(__file__)[0])
if path not in sys.path:
    sys.path.append(path)

#raise RuntimeError('sys.path = ' + '\n'.join(sys.path)) 


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

#path = os.path.abspath(os.path.split(__file__)[0])
#if path not in sys.path:
#    sys.path.append(path)

