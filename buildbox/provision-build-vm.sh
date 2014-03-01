yum install -y java-1.7.0-openjdk.x86_64 lsof wget nc ruby rubygems ruby-devel rpm-build

gem install fpm 

sudo cp /mnt/saboteur/buildbox/.vimrc /home/vagrant
chown vagrant:vagrant /home/vagrant/.vimrc
