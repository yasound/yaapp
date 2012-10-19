#!/bin/sh

# create /data/ folders
mkdir /data/logs
mkdir /data/tmp
mkdir /data/var
mkdir /data/var/lib
mkdir /data/var/lib/celery

# change rights to customer
chown customer:customer /data/logs
chown customer:customer /data/tmp
chown customer:customer /data/var/lib/celery

# copy files
cp ./etc/init.d/* /etc/init.d
cp ./etc/default/* /etc/default/
cp -r ./etc/gunicorn /etc/
cp ./etc/nginx/sites-available/yaapp /etc/nginx/sites-available/

# ffmpeg static binary
cp ./bin/ffmpeg /usr/local/bin/

# nginx configuration
cd /etc/nginx/sites-enabled
ln -s ../sites-available/yaapp yaapp


