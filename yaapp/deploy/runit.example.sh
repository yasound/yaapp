#!/bin/sh

GUNICORN=../vtenv/bin/gunicorn
PID=/var/run/django_sample_env.pid
USER=yasound
APP=wsgi
DIR=/var/www/dev.yasound.com/root/yaapp

if [ -f $PID ]; then rm $PID; fi

cd $DIR
exec sudo -H -u $USER DJANGO_MODE="development" $GUNICORN $APP
