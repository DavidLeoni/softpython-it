#!/bin/bash

# Example to show all the steps to create and publish an exam

########  Just some book-keeping for the script, ignore it.
set -e
if [ -d "private/2000-12-31" ] || [ -d "past-exams/2000-12-31" ] ; then
    echo
    echo "  ERROR: example exam '2000-12-31' already exists ! You can safely delete it with "
    echo
    echo "      python3 exam.py delete 2000-12-31"
    echo
    exit 1
fi
# Makes the bash script to print out every command before it is executed except echo
trap '[[ $BASH_COMMAND != echo* ]] && echo $BASH_COMMAND' DEBUG

###### end bookkeeping  #####################################


python3 exam.py init 2000-12-31
python3 exam.py package 2000-12-31

echo
echo "------- Simulating some shipped exams..."
mkdir -p private/2000-12-31-admin/shipped/john-doe-112233
cp jm-templates/exam-solutions/*.py private/2000-12-31-admin/shipped/john-doe-112233
mkdir -p private/2000-12-31-admin/shipped/jane-doe-445566
cp jm-templates/exam-solutions/*.py private/2000-12-31-admin/shipped/jane-doe-445566
echo "------- Done with shipped exams simulation, time to grade ..."
echo

python3 exam.py grade 2000-12-31
python3 exam.py zip-grades 2000-12-31
python3 exam.py publish 2000-12-31

echo
echo '  Finished example exam run !!'
echo


