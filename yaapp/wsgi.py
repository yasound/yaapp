import os,sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yaapp.settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.

#path = os.path.abspath(os.path.split(__file__)[0])
path = '/home/meeloo/work/yaapp' #os.path.abspath(os.path.split(__file__)[0])
if path not in sys.path:
    sys.path.append(path)

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

#path = os.path.abspath(os.path.split(__file__)[0])
#if path not in sys.path:
#    sys.path.append(path)

