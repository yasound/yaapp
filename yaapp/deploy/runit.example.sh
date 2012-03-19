#!/bin/sh

GUNICORN=../vtenv/bin/gunicorn
PID=/var/run/dev.yasound.com.pid
USER=yasound
APP=deploy
DIR=/var/www/dev.yasound.com/root/yaapp

if [ -f $PID ]; then rm $PID; fi

cd $DIR
exec sudo -H -u $USER DJANGO_MODE="production" $GUNICORN $APP
