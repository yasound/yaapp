#!/bin/sh
export DJANGO_SETTINGS_MODULE=settings
make html
doc2dash --name yaapp --force -A _build/html/ -i ../media/images/logos/yasound-inline-grey.png
