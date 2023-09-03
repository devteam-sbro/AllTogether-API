#!/bin/sh

DIR_HOME=$(pwd)

export PYTHONPATH="${PYTHONPATH}:$DIR_HOME"

python3 backend/manage.py $1 $2
