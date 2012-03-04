# REALLY UGLY THING
# =================
import os, sys
from os.path import abspath, dirname, join
deploy =  os.path.join(abspath(dirname(__file__)), 'deploy.wsgi')
execfile(deploy)
