#!/bin/bash

apt-get update
apt-get --assume-yes install linux-tools-common 
apt-get --assume-yes install linux-tools-generic linux-cloud-tools-generic 
apt-get --assume-yes  install linux-tools-`uname -r`
apt-get --assume-yes install build-essential

perf list