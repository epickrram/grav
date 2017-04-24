#!/bin/bash

set -e -u -o pipefail

SCRIPT_DIR=$(dirname "$0")

PID="${1:-}"

if [[ "$PID" == "" ]]; then
  echo "Please supply pid as first parameter"
  exit 1
fi

source $SCRIPT_DIR/validate-perf-map-agent.sh
source $SCRIPT_DIR/options-perf-thread-flames.sh

jstack $1 > $JSTACKS
$PERF_MAP_AGENT_DIR/bin/perf-java-record-stack $*
sudo perf script -i $PERF_DATA_FILE > $STACKS
$FLAMEGRAPH_DIR/stackcollapse-perf.pl $PERF_COLLAPSE_OPTS $STACKS > $COLLAPSED
python $GRAV_DIR/src/flames/convert_tid_stacks.py $JSTACKS $COLLAPSED $COLLAPSED_WITH_THREADS
cat $COLLAPSED_WITH_THREADS | $FLAMEGRAPH_DIR/flamegraph.pl $PERF_FLAME_OPTS > $PERF_FLAME_OUTPUT

