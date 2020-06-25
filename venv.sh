#!/usr/bin/bash
set -ex
python3 -m virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
./run.py $1
