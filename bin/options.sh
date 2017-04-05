#/bin/bash

set -e -u -o pipefail


if [[ "${PERF_DATA_DIR:-}" == "" ]];then
    PERF_DATA_DIR="/tmp"
fi

if [[ "${PERF_DATA_FILE:-}" == "" ]];then
    PERF_DATA_FILE="$PERF_DATA_DIR/perf-$PID.data"
fi

if [[ "${PERF_SCRIPT_FILE:-}" == "" ]];then
    PERF_SCRIPT_FILE="$PERF_DATA_DIR/perf-script-$PID.txt"
fi

if [[ "${PERF_SAMPLE_FREQUENCY:-}" == "" ]];then
    PERF_SAMPLE_FREQUENCY=99
fi


if [[ "${PERF_RECORD_DURATION:-}" == "" ]];then
    PERF_RECORD_DURATION=5
fi
