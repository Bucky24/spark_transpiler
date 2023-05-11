#!/bin/bash

if [[ $# -eq 0 ]]; then
    echo "Usage: spark <file to compile>"
    exit 1
fi

# from https://stackoverflow.com/a/1638397/8346513
# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

node $SCRIPTPATH/spark.js $@