# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"


  config.vm.provision :shell, path: "install-jdk8.sh"
  config.vm.provision :shell, path: "install-perf.sh"
  config.vm.provision :shell, path: "init.sh"

  config.vm.network :forwarded_port, guest: 8080, host: 18080
  
end
