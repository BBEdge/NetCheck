#!/usr/bin/bash

source venv/bin/activate

python srvconnect.py

python app.py > app.log 2>&1 &