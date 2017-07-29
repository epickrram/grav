#!/bin/bash



# download dependent projects

apt-get --assume-yes install git
cd /vagrant
git  clone https://github.com/jvm-profiling-tools/perf-map-agent.git
git  clone https://github.com/brendangregg/FlameGraph.git
git  clone https://github.com/epickrram/grav.git

# set ENV VARS for vagrant when its up
[ -f ~/.profile ] || touch /home/vagrant/.profile
echo "export PERF_MAP_AGENT_DIR=/vagrant/perf-map-agent" >> /home/vagrant/.profile
echo "export FLAMEGRAPH_DIR=/vagrant/FlameGraph" >> /home/vagrant/.profile
echo "export GRAV_DIR=/vagrant/grav" >> /home/vagrant/.profile
echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/" >> /home/vagrant/.profile


echo -1 > /proc/sys/kernel/perf_event_paranoid

# make perf-map-agent

export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
apt-get --assume-yes install cmake
cd /vagrant/perf-map-agent
cmake .
make clean
make

