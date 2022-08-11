#!/bin/bash
set -e

#note: tou can't specify a python version to venv, so you need to run with an installed python

DIR=_private/jupman_env
if [ $# -eq 0 ]
  then
    PYTHONCMD=python3
  else
    PYTHONCMD=$1
fi


COMMAND="$PYTHONCMD -m venv $DIR"


if [ -d "$DIR" ]; then
    echo    
    echo "ERROR: Directory  $DIR already exists, aborting..."
    echo
    exit
fi

echo $COMMAND
$COMMAND
echo "source  $DIR/bin/activate"
source  $DIR/bin/activate
set -o xtrace
python3 -m pip install --upgrade pip
python3 -m pip install  -r requirements-build.txt
python3 -m pip install  -r _test/requirements-test.txt

set +o xtrace
echo deactivate
deactivate

