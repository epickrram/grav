#/bin/bash

set -e -u -o pipefail

if [[ "${PERF_MAP_AGENT_DIR:-}" == "" ]]; then
    echo "Please set environment variable PERF_MAP_AGENT_DIR to the location of your local clone of https://github.com/perf-map-agent"
    exit 1
fi
