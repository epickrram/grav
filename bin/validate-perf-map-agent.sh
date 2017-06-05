#!/bin/bash

set -e -u -o pipefail

if [[ "${PERF_MAP_AGENT_DIR:-}" == "" ]]; then
    echo "Cannot determine location of perf-map-agent repository"
    echo "Please set PERF_MAP_AGENT_DIR to point to the root of the git repository"
    exit 1
fi

if [[ "${FLAMEGRAPH_DIR:-}" == "" ]]; then
    echo "Cannot determine location of flamegraph repository"
    echo "Please set FLAMEGRAPH_DIR to point to the root of the git repository"
    exit 1
fi

JSTACK="$(which jstack)"

if [[ "$JSTACK" == "" ]]; then
    echo "Cannot find the jstack executable on PATH"
    echo "Please add JDK_HOME/bin to your PATH"
    exit 1
fi

