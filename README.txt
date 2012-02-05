Yaapp Django application

Useful environment variables to setup:

* DJANGO_MODE = 'production' | 'development'
* USE_MYSQL = 1 to connect to mysql instance on local mode

How to launch shell on prod server :

* sudo DJANGO_MODE='production' ./manage.py shell_plus

How to restart server:
* /etc/init.d/yaapp restart && /etc/init.d/celeryd restart
