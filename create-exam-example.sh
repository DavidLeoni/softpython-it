#!/bin/bash

# Example to show all the steps to create and publish an exam

set -e

if [ -d "private/exams/2000-12-31" ]; then
    echo
    echo "  ERROR: exam '2000-12-31' already exists ! You can delete it with "
    echo
    echo "      ./exam.py delete 2000-12-31"
    echo
    exit 1
fi

./exam.py init 2000-12-31
./exam.py package 2000-12-31
./exam.py grade 2000-12-31
./exam.py zip-grades 2000-12-31
./exam.py copy-exam 2000-12-31
echo "git add ."
echo "git commit -m 'published exam'"
echo "git push"


