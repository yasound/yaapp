#!/bin/sh
echo "Creating directories for local mongo"
mkdir mongo_data/db
mkdir mongo_data/logs

echo "Creating env"
./vtenv.sh

cd yaapp
./manage.py validate
./manage.py collectstatic --noinput
./manage.py syncdb --noinput
./manage.py migrate
echo "Creating super user"
./manage.py createsuperuser

echo "Done."