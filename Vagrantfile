# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

    config.vm.define "buildbox" do |host|
        host.vm.hostname = "buildbox"
        host.vm.box = "centos64"
        host.vm.box_url = "https://github.com/2creatives/vagrant-centos/releases/download/v0.1.0/centos64-x86_64-20131030.box"

        host.vm.network :private_network, ip: "192.168.2.199"

        host.vm.synced_folder ".", "/mnt/saboteur"

        host.vm.provider :virtualbox do |vb|
           vb.customize ["modifyvm", :id, "--memory", "512"]
        end

        host.vm.provision "shell", path: "buildbox/provision-build-vm.sh"
    end

    config.vm.define "ubuntu1210" do |host|
        host.vm.hostname = "ubuntu1210"
        host.vm.box = "ubuntu1210_64"
        host.vm.box_url = "https://github.com/downloads/roderik/VagrantQuantal64Box/quantal64.box"

        host.vm.network :private_network, ip: "192.168.2.201"

        host.vm.synced_folder ".", "/mnt/saboteur"

        host.vm.provider :virtualbox do |vb|
           vb.customize ["modifyvm", :id, "--memory", "256"]
        end
    end

    config.vm.define "fedora19" do |host|
        host.vm.hostname = "fedora19"
        host.vm.box = "fedora19_64"
        host.vm.box_url = "https://dl.dropboxusercontent.com/u/86066173/fedora-19.box"

        host.vm.network :private_network, ip: "192.168.2.202"

        host.vm.synced_folder ".", "/mnt/saboteur"

        host.vm.provider :virtualbox do |vb|
           vb.customize ["modifyvm", :id, "--memory", "256"]
        end
    end
end
