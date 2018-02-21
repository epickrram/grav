#!/bin/bash

#sudo apt-get update
#sudo apt-get  --assume-yes install python-bpfcc

#echo "deb [trusted=yes] https://repo.iovisor.org/apt/xenial xenial-nightly main" | sudo tee /etc/apt/sources.list.d/iovisor.list
#sudo apt-get update
#sudo apt-get --assume-yes install bcc-tools libbcc-examples


sudo apt-get -y install bison build-essential cmake flex git libedit-dev \
  libllvm3.7 llvm-3.7-dev libclang-3.7-dev python zlib1g-dev libelf-dev
# For Lua support
sudo apt-get -y install luajit luajit-5.1-dev

git clone https://github.com/iovisor/bcc.git
mkdir bcc/build; cd bcc/build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr
make clean
make
sudo make install

sudo apt-get --assume-yes install build-essential linux-headers-`uname -r`




