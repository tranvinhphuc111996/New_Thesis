#!/bin/bash

rm database.db
python database.py

export FLASK_ENV=development
export FLASK_APP=main.py

flask run --host=0.0.0.0
