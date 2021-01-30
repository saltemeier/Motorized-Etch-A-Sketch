#!/bin/bash

export FLASK_APP=/home/pi/EAS/flask/EAS_flask_v2.py
#export FLASK_ENV=development
#export FLASK_ENV=production
python3 -m flask run --host=0.0.0.0

