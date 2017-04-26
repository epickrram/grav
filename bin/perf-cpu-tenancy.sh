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
JSTACK_FILE="$PERF_DATA_DIR/jstack-$PID.txt"
jstack "$PID" > $JSTACK_FILE

echo "Recording samples.."

sudo perf record -F "$PERF_SAMPLE_FREQUENCY" -o "$PERF_DATA_FILE" -e cycles -a -- sleep "$PERF_RECORD_DURATION"
sudo perf script -i "$PERF_DATA_FILE" -F comm,pid,tid,cpu,time,event | grep -E "\s+$PID" > "$PERF_SCRIPT_FILE"

cat "$PERF_SCRIPT_FILE" | python "$SCRIPT_DIR/../src/cpu/cpu_tenancy.py" "$PID" "$JSTACK_FILE"

sudo rm "$PERF_DATA_FILE"
