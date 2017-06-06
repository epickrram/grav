#!/bin/bash

apt-get update
apt-get --assume-yes install linux-tools-common 
apt-get --assume-yes install linux-tools-generic linux-cloud-tools-generic
apt-get --assume-yes install linux-tools-3.13.0-77-generic linux-cloud-tools-3.13.0-77-generic
apt-get --assume-yes install build-essential

perf list