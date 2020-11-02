#!/usr/bin/bash

source venv/bin/activate

python app.py > app.log 2>&1 &