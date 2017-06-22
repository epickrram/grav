# grav

A collection of tools to help visualise process execution.

This [blog post](https://epickrram.blogspot.co.uk/2017/05/performance-visualisation-tools.html) has some detail on the rationale and implementation detail.

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

### vagrant-grav

A Vagrant box that can be used as a grav development environment on non-linux machines.

Pre-requisite: 
 - [vagrant](https://www.vagrantup.com/)

Usage:
```
$ cd vagrant-grav
$ vagrant up
```

will run a vagrant box with:
1. ubuntu trusty64
1. Java OpenJDK8
1. perf
1. [perf-map-agent](https://github.com/jvm-profiling-tools/perf-map-agent)
1. [FlameGraph](https://github.com/brendangregg/Flamegraph) scripts
1. grav scripts

```
$ vagrant ssh 
...
vagrant@vagrant-ubuntu-trusty-64:~$ echo $JAVA_HOME
/usr/lib/jvm/java-8-openjdk-amd64/
vagrant@vagrant-ubuntu-trusty-64:~$ echo $GRAV_DIR
/vagrant/grav
vagrant@vagrant-ubuntu-trusty-64:~$ echo $FLAMEGRAPH_DIR
/vagrant/FlameGraph
vagrant@vagrant-ubuntu-trusty-64:~$ echo $PERF_MAP_AGENT_DIR
/vagrant/perf-map-agent
```

The VM is now ready for grav development.
```
vagrant@vagrant-ubuntu-trusty-64:~$ logout
Connection to 127.0.0.1 closed.
$ vagrant port
The forwarded ports for the machine are listed below. Please note that
these values may differ from values configured in the Vagrantfile if the
provider supports automatic port collision detection and resolution.

    22 (guest) => 2200 (host)
  8080 (guest) => 18080 (host)
```
 Forwarded port 8080 to port 18080 to allow access to a server running inside the box.
 

### Maintainers

[Mark Price](https://github.com/epickrram)

[Amir Langer](https://github.com/langera)

