import os.path
from fabric.api import *
from fabric.utils import puts
from fabric.contrib.files import sed, uncomment, append, exists

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
    with cd(WEBSITE_PATH):
        run("git checkout master")
        run("git pull")
        run("./vtenv.sh")
    with cd("%s/%s" % (WEBSITE_PATH, APP_PATH)):
        run("DJANGO_MODE='production' ./manage.py collectstatic --noinput")
        if not exists("./media/cache"):
            run("ln -s /data/glusterfs-mnt/replica2all/front/cache ./media/cache")
        if not exists("./media/pictures"):
            run("ln -s /data/glusterfs-mnt/replica2all/front/pictures ./media/pictures")
        if not exists("./media/covers"):
            run("mkdir ./media/covers/")
        if not exists("./media/covers/albums"):
            run("ln -s /data/glusterfs-mnt/replica2all/album-cover ./media/covers/albums")
        if not exists("./media/covers/songs"):
            run("ln -s /data/glusterfs-mnt/replica2all/song-cover ./media/covers/songs")
        run("/etc/init.d/yaapp restart")
        run("/etc/init.d/celeryd restart")
        run("/etc/init.d/celerybeat restart")

