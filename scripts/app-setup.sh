#!/usr/bin/env bash

pip3 install -r requirements.txt


[ ! -d "./alembic" ] && echo "Running 'alembic innit alembic'..."
[ -d "./alembic" ] && echo "alembic already innitialized, skipping..."
[ ! -d "./alembic" ] && alembic init alembic

python3 run.py