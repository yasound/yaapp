#!/bin/sh


# copy files
cp ./etc/init.d/* /etc/init.d
cp ./etc/default/* /etc/default/
cp -r ./gunicorn /etc/
cp ./etc/nginx/sites-available/yaapp /etc/nginx/sites-available/

# nginx
cd /etc/nginx/sites-enabled
ln -s yaapp ../sites-available/yaapp
