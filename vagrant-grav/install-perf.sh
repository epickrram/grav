#!/bin/bash

apt-get update
apt-get --assume-yes install linux-tools-common 
apt-get --assume-yes install linux-tools-generic linux-cloud-tools-generic
apt-get --assume-yes install linux-tools-4.10.0-28-generic linux-cloud-tools-4.10.0-28-generic
#apt-get --assume-yes install linux-tools-4.4.0-81-generic linux-cloud-tools-4.4.0-81-generic
apt-get --assume-yes install build-essential

perf list