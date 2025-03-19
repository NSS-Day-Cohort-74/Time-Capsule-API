#!/bin/bash

rm db.sqlite3
rm -rf ./timecapsuleapi/migrations
python3 manage.py migrate
python3 manage.py makemigrations timecapsuleapi
python3 manage.py migrate timecapsuleapi
python3 manage.py loaddata users
python3 manage.py loaddata tokens

