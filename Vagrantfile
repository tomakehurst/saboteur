# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

    config.vm.define "buildbox" do |host|
        host.vm.hostname = "buildbox"
        host.vm.box = "centos64min"
        host.vm.box_url = "https://github.com/2creatives/vagrant-centos/releases/download/v0.1.0/centos64-x86_64-20131030.box"

        host.vm.network :private_network, ip: "192.168.2.99"

        host.vm.synced_folder ".", "/mnt/breakbox"

        host.vm.provider :virtualbox do |vb|
           vb.customize ["modifyvm", :id, "--memory", "512"]
        end

        host.vm.provision "shell", path: "buildbox/provision-build-vm.sh"
    end
end
