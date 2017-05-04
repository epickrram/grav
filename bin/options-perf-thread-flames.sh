if [ "${PERF_JAVA_TMP:-}" == "" ]; then
    PERF_JAVA_TMP=/tmp
fi

PERF_COLLAPSE_OPTS="--kernel --tid"
PERF_MAP_OPTIONS="unfoldall"
PERF_FLAME_OPTS="--color=java"
STACKS=$PERF_JAVA_TMP/out-$PID.stacks
JSTACKS=$PERF_JAVA_TMP/out-$PID.jstacks
COLLAPSED=$PERF_JAVA_TMP/out-$PID.collapsed
COLLAPSED_WITH_THREADS=$PERF_JAVA_TMP/out-threads-$PID.collapsed
GRAV_DIR=$(dirname $(readlink -f $0))/..
AGGREGATE_ON_THREAD_PREFIX="${AGGREGATE_ON_THREAD_PREFIX:-False}"

if [ "${PERF_DATA_FILE:-}" == "" ]; then
    PERF_DATA_FILE=$PERF_JAVA_TMP/perf-$PID.data
fi

if [ "${PERF_FLAME_OUTPUT:-}" == "" ]; then
    PERF_FLAME_OUTPUT=flamegraph-$PID.svg
fi


