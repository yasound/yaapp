#!/bin/sh

GUNICORN=../vtenv/bin/gunicorn
PID=./dev.yasound.com.pid
DIR=/var/www/dev.yasound.com/root/yaapp

APP=deploy

if [ -f $PID ]; then rm $PID; fi

cd $DIR
exec sudo -H -u yasound DJANGO_MODE="production" $GUNICORN --debug $APP --pid $PID
