import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yaapp.settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

path = os.path.abspath(os.path.split(__file__)[0])
if path not in sys.path:
    sys.path.append(path)

