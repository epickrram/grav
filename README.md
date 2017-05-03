# grav

A collection of tools to help visualise process execution.

### Scheduler profile

Visual cues to inform whether your application's threads are being pre-empted by the kernel scheduler before they are ready to yield the processor.

![Scheduler Profile](https://github.com/epickrram/blog-images/raw/master/2017_04/scheduler-profile.png)

Pre-requisites: install [iovisor BCC](https://github.com/iovisor/bcc)

Usage:

```
$ ./bin/scheduling-profile.sh $PID
Recording scheduling information for 15 seconds
Wrote scheduler-profile-$PID.svg
```

### CPU tenancy

Determine whether application threads would be better restricted to a certain set of CPUs.

![CPU Tenancy](https://github.com/epickrram/blog-images/raw/master/2017_04/cpu-tenancy.png)

Pre-requisites: install [perf_events](https://perf.wiki.kernel.org/index.php/Main_Page)

Usage:

```
$ ./bin/perf-cpu-tenancy.sh $PID
Recording samples..
Wrote cpu-tenancy-$PID.svg
```

### Java flamegraphs with thread name

Annotate JVM flamegraphs with thread names for easier focus.

![Named threads](https://github.com/epickrram/blog-images/raw/master/2017_04/gc_threads_flamegraph.png)

Pre-requisites: the following repositories need to be cloned and available locally:

   * [perf-map-agent](https://github.com/jvm-profiling-tools/perf-map-agent)
   * [flamegraph](https://github.com/brendangregg/Flamegraph)

Usage:

```
# set up environment variables
$ export PERF_MAP_AGENT_DIR=/path/to/perf-map-agent/
$ export FLAMEGRAPH_DIR=/path/to/flamegraph/
$ ./bin/perf-thread-flames.sh $PID
Recording events for 15 seconds (adapt by setting PERF_RECORD_SECONDS)
[ perf record: Woken up 1 times to write data ]
[ perf record: Captured and wrote 0.343 MB /tmp/perf-$PID.data (835 samples) ]
Wrote flamegraph-$PID.svg
```

To filter out particular threads, supply a regex as the second argument:

```
$ ./bin/perf-thread-flames.sh $PID ".*GC.*"
Capturing stacks for threads matching '.*GC.*'
Recording events for 15 seconds (adapt by setting PERF_RECORD_SECONDS)
[ perf record: Woken up 7 times to write data ]
[ perf record: Captured and wrote 1.026 MB /tmp/perf-$PID.data (496 samples) ]
Wrote flamegraph-$PID.svg
```

### Maintainer

[Mark Price](https://github.com/epickrram)