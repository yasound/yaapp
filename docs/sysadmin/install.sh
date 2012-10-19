#!/bin/sh


# copy files
cp ./etc/init.d/* /etc/init.d
cp ./etc/default/* /etc/default/
cp -r ./etc/gunicorn /etc/
cp ./etc/nginx/sites-available/yaapp /etc/nginx/sites-available/

# ffmpeg
cp ./bin/ffmpeg /usr/local/bin/

# nginx
cd /etc/nginx/sites-enabled
ln -s ../sites-available/yaapp yaapp


