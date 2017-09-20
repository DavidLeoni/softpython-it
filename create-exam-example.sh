#!/bin/bash

# Example to show all the steps to create and publish an exam

set -e
if [ -d "private/2000-12-31" ]; then
    echo
    echo "  ERROR: example exam '2000-12-31' already exists ! You can safely delete it with "
    echo
    echo "      ./exam.py delete 2000-12-31"
    echo
    exit 1
fi

python exam.py init 2000-12-31
python exam.py package 2000-12-31

# simulating some shipped exams...
mkdir -p private/2000-12-31/shipped/john-doe-112233
cp templates/exam/exercises/* private/2000-12-31/shipped/john-doe-112233
mkdir -p private/2000-12-31/shipped/jane-doe-445566
cp templates/exam/exercises/* private/2000-12-31/shipped/jane-doe-445566
# done with the simulation, time to grade

python exam.py grade 2000-12-31
python exam.py zip-grades 2000-12-31
python exam.py publish 2000-12-31

echo
echo '  Finished example exam run !!'
echo


