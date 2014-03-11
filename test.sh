#!/bin/bash

#####
#
# This script builds the project, and runs the tests.
#
# Example usage:
# ./test.sh
#   ( runs all tests )
# ./test.sh -LE SLOW -VV
#   ( runs only fast tests, verbose output )
# ./test.sh -R clic -VV
#   ( runs tests where name is matching regular expression 'clic' )
# ./test.sh -N
#   ( only lists the test names without running them )
#
######


python setup.py build
for f in `pwd`/build/lib*
do
    PYTHONPATH=$PYTHONPATH:$f
done
echo "PYTHONPATH: $PYTHONPATH"
PYTHONPATH=$PYTHONPATH ctest $@
