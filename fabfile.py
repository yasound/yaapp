import os.path
from fabric.api import *
from fabric.utils import puts
from fabric.contrib.files import sed, uncomment, append, exists


def prod():
    global WEBSITE_PATH
    global APP_PATH
    global GIT_PATH
    global BRANCH
    global DJANGO_MODE

    env.forward_agent = 'True'
    env.hosts = [
        'yas-web-08.ig-1.net',
        'yas-web-09.ig-1.net',
    ]
    env.user = "customer"
    WEBSITE_PATH = "/data/vhosts/y/yasound.com/root/"
    APP_PATH = "yaapp"
    GIT_PATH = "git@github.com:yasound/yaapp.git"
    BRANCH = "master"
    DJANGO_MODE = 'production'

def filers():
    global WEBSITE_PATH
    global APP_PATH
    global GIT_PATH
    global BRANCH
    global DJANGO_MODE

    env.forward_agent = 'True'
    env.hosts = [
        'yas-filer-01',
        'yas-filer-02',
    ]
    env.user = "customer"
    WEBSITE_PATH = "/data/vhosts/y/yasound.com/root/"
    APP_PATH = "yaapp"
    GIT_PATH = "git@github.com:yasound/yaapp.git"
    BRANCH = "master"
    DJANGO_MODE = 'production'

def dev():
    global WEBSITE_PATH
    global APP_PATH
    global GIT_PATH
    global BRANCH
    global DJANGO_MODE
    env.forward_agent = 'True'
    env.hosts = [
        'yas-dev-01.ig-1.net',
        'yas-dev-02.ig-1.net',
    ]
    env.user = "customer"
    WEBSITE_PATH = "/data/vhosts/y/yasound.com/root/"
    APP_PATH = "yaapp"
    GIT_PATH = "git@github.com:yasound/yaapp.git"
    BRANCH = "dev"
    DJANGO_MODE = 'development'


def deploy():
    """[DISTANT] Update distant django env
    """
    with cd(WEBSITE_PATH):
        run("git checkout %s" % (BRANCH))
        run("git pull")
        run("./vtenv.sh")
    with cd("%s/%s" % (WEBSITE_PATH, APP_PATH)):
        run("DJANGO_MODE='%s' ./manage.py collectstatic --noinput" % (DJANGO_MODE))
        if DJANGO_MODE == 'production':
            if not exists("./media/cache"):
                run("ln -s /data/glusterfs-mnt/replica2all/front/cache ./media/cache")
            if not exists("./media/compressed"):
                run("ln -s /data/glusterfs-mnt/replica2all/front/compressed ./media/compressed")
            if not exists("./media/pictures"):
                run("ln -s /data/glusterfs-mnt/replica2all/front/pictures ./media/pictures")
            if not exists("./media/user_pictures"):
                run("ln -s /data/glusterfs-mnt/replica2all/front/user_pictures ./media/user_pictures")
            if not exists("./media/radio_pictures"):
                run("ln -s /data/glusterfs-mnt/replica2all/front/radio_pictures ./media/radio_pictures")
            if not exists("./media/covers"):
                run("mkdir ./media/covers/")
            if not exists("./media/covers/albums"):
                run("ln -s /data/glusterfs-mnt/replica2all/album-cover ./media/covers/albums")
            if not exists("./media/covers/songs"):
                run("ln -s /data/glusterfs-mnt/replica2all/song-cover ./media/covers/songs")
            if not exists("./media/radioways"):
                run("ln -s /data/glusterfs-mnt/replica2all/front/radioways ./media/radioways")

        elif DJANGO_MODE == 'development':
            if not exists("./media/cache"):
                run("ln -s /data/storage/front/cache ./media/cache")
            if not exists("./media/compressed"):
                run("ln -s /data/storage/front/compressed ./media/compressed")
            if not exists("./media/pictures"):
                run("ln -s /data/storage/front/pictures ./media/pictures")
            if not exists("./media/user_pictures"):
                run("ln -s /data/storage/front/user_pictures ./media/user_pictures")
            if not exists("./media/radio_pictures"):
                run("ln -s /data/storage/front/radio_pictures ./media/radio_pictures")
            if not exists("./media/covers"):
                run("mkdir ./media/covers/")
            if not exists("./media/covers/albums"):
                run("ln -s /data/storage/album-cover ./media/covers/albums")
            if not exists("./media/covers/songs"):
                run("ln -s /data/storage/song-cover ./media/covers/songs")
            if not exists("./media/radioways"):
                run("ln -s /data/storage/front/radioways ./media/radioways")

        run("DJANGO_MODE='%s' ./manage.py compress" % (DJANGO_MODE))
        run("/etc/init.d/yaapp restart")
        run("/etc/init.d/celeryd restart")
        run("/etc/init.d/celerybeat restart")
    if env.host_string == 'yas-web-08.ig-1.net':
        with cd(WEBSITE_PATH):
            run("./fab filers deploy")


def update():
    """[DISTANT] Update distant django env
    """
    with cd(WEBSITE_PATH):
        run("git checkout %s" % (BRANCH))
        run("git pull")
        run("./vtenv.sh")
    with cd("%s/%s" % (WEBSITE_PATH, APP_PATH)):
        run("DJANGO_MODE='%s' ./manage.py collectstatic --noinput" % (DJANGO_MODE))
        run("DJANGO_MODE='%s' ./manage.py compress" % (DJANGO_MODE))
        run("/etc/init.d/yaapp restart")


def restart_all():
    """[DISTANT] restart services
    """
    with cd("%s/%s" % (WEBSITE_PATH, APP_PATH)):
        run("/etc/init.d/yaapp restart")
        run("/etc/init.d/celeryd restart")
        run("/etc/init.d/celerybeat restart")


def restart_celery():
    """[DISTANT] restart services
    """
    with cd("%s/%s" % (WEBSITE_PATH, APP_PATH)):
        run("/etc/init.d/celeryd restart")
        run("/etc/init.d/celerybeat restart")


def test():
    """[DISTANT] restart services
    """
    with cd("%s/%s" % (WEBSITE_PATH, APP_PATH)):
        run("ls")
