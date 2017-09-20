#!/bin/bash

# Example to show all the steps to create and publish an exam

set -e

if [ -d "private/exams/2000-12-31" ]; then
    echo
    echo "  ERROR: test exam '2000-12-31' already exists ! You can delete it with "
    echo
    echo "      ./exam.py delete 2000-12-31"
    echo
    exit 1
fi

python exam.py init 2000-12-31
python exam.py package 2000-12-31
python exam.py grade 2000-12-31
python exam.py zip-grades 2000-12-31
python exam.py copy-exam 2000-12-31
echo 
echo "You could now run manually the following git instructions to publish the exam:"
echo "git add ."
echo "git commit -m 'published exam'"
echo "git push"


