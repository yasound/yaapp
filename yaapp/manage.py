#!/usr/bin/env python
import sys

import os
from os.path import abspath, dirname, join

PROJECT_ROOT = abspath(dirname(__file__))

# Uncomment this if you use Virtualenv
#
activate_this = PROJECT_ROOT + "/../vtenv/bin/activate_this.py"
execfile(activate_this, dict(__file__=activate_this))

sys.path.insert(0, join(PROJECT_ROOT, "apps"))


if not os.environ.has_key('DJANGO_MODE'): 
    os.environ['DJANGO_MODE'] = 'local'
    print "------------------------------------------------------------------------------"
    print " Manage in LOCAL mode : set DJANGO_MODE env variable for prod and dev servers."
    print " See README for more informations"
    print "------------------------------------------------------------------------------"
    from time import sleep
    sleep(1)

from django.core.management import execute_manager
import imp
try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

import settings

if __name__ == "__main__":
    execute_manager(settings)
