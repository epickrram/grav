#!/bin/bash

set -e -u -o pipefail

SCRIPT_DIR=$(dirname "$0")
source $SCRIPT_DIR/validate.sh

PID="${1:-}"

if [[ "$PID" == "" ]]; then
    echo "Please supply pid as first parameter"
    exit 1
fi


source $SCRIPT_DIR/options.sh
source $SCRIPT_DIR/functions.sh

export PID

check_command_contains_java

if [[ "$COMMAND_CONTAINS_JAVA" != "" ]]; then
    JSTACK_FILE="$PERF_DATA_DIR/jstack-$PID.txt"
    jstack "$PID" > $JSTACK_FILE
else
    JSTACK_FILE="/dev/null"
fi


echo "Recording scheduling information for $PERF_RECORD_DURATION seconds"

sudo python "$SCRIPT_DIR/../src/cpu/bcc_scheduler_profile.py" "$PID" "$PERF_RECORD_DURATION" "$PERF_DATA_DIR/scheduler-states-$PID.json" "$PERF_DATA_DIR/contending-commands-$PID.json"

cat "$PERF_DATA_DIR/scheduler-states-$PID.json" | python "$SCRIPT_DIR/../src/cpu/scheduler_profile.py" "$JSTACK_FILE" "$PID"
#cat "$PERF_DATA_DIR/contending-commands-$PID.json" | python "$SCRIPT_DIR/../src/cpu/contending_commands_profile.py" "$PID"

