#!/bin/bash

if [ "${PERF_JAVA_TMP:-}" == "" ]; then
    PERF_JAVA_TMP=/tmp
fi

ADDITIONAL="${1:-}"

if [[ "$ADDITIONAL" != "" ]]; then
    ADDITIONAL="-$ADDITIONAL"
fi

PERF_COLLAPSE_OPTS="--kernel --tid"
PERF_MAP_OPTIONS="unfoldall"
PERF_FLAME_OPTS="--color=java"
STACKS=$PERF_JAVA_TMP/out-$PID$ADDITIONAL.stacks
JSTACKS=$PERF_JAVA_TMP/out-$PID$ADDITIONAL.jstacks
COLLAPSED=$PERF_JAVA_TMP/out-$PID$ADDITIONAL.collapsed
COLLAPSED_WITH_THREADS_PREFIX=out-threads-$PID
COLLAPSED_WITH_THREADS=$PERF_JAVA_TMP/$COLLAPSED_WITH_THREADS_PREFIX$ADDITIONAL.collapsed
GRAV_DIR=$(dirname $(readlink -f $0))/..
AGGREGATE_ON_THREAD_PREFIX="${AGGREGATE_ON_THREAD_PREFIX:-False}"

if [ "${PERF_DATA_FILE:-}" == "" ]; then
    PERF_DATA_FILE=$PERF_JAVA_TMP/perf-$PID.data
fi

if [ "${PERF_FLAME_OUTPUT:-}" == "" ]; then
    PERF_FLAME_OUTPUT=flamegraph-$PID.svg
fi


