import os.path
from fabric.api import *
from fabric.utils import puts
from fabric.contrib.files import sed, uncomment, append

env.hosts = [
    'yas-web-01.ig-1.net',
    'yas-web-02.ig-1.net',
    'yas-web-03.ig-1.net',
    'yas-web-04.ig-1.net',
    'yas-web-05.ig-1.net',
    'yas-web-06.ig-1.net',
    'yas-web-07.ig-1.net',
    'yas-web-08.ig-1.net',
    'yas-web-09.ig-1.net',
    'yas-web-10.ig-1.net',
]
env.user = "customer"

WEBSITE_PATH = "/data/vhosts/y/yasound.com/root/"
APP_PATH = "yaapp"
GIT_PATH = "git@github.com:yasound/yaapp.git"
BRANCH = "iguane"

def test():
    """Test application
    """
    local('cd yaapp &&./manage.py test')

def collectstatic():
    """Command collect static
    """
    with lcd("%s" % WEBSITE_PATH):
        local('./manage.py collectstatic --noinput')

def deploy():
    """[DISTANT] Update distant django env
    """
    test()
    with cd(WEBSITE_PATH):
        run("git pull")
        run("./vtenv.sh")
    with cd("%s/%s" % (WEBSITE_PATH, APP_PATH)):
        run("./manage.py collectstatic --noinput")
        run("/etc/init.d/yaapp restart")
        run("/etc/init.d/celeryd restart")
        run("/etc/init.d/celerybeat restart")

