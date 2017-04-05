#/bin/bash

set -e -u -o pipefail

JSTACK=$(which jstack)

if [[ "$JSTACK" == "" ]]; then
    echo "Cannot find the jstack executable on PATH"
    echo "Please add JDK_HOME/bin to your PATH"
    exit 1
fi
