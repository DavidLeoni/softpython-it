#!/bin/bash
set -e

DIR=_private/softpython_it_env
#note: tou can't specify a python version to venv, so I'm running it with exactly the python I have installed
COMMAND="python3.7 -m venv $DIR"


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

