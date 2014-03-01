#!/usr/bin/env sh

[ -f /etc/init.d/saboteur-agent ] && service saboteur-agent stop

sudo id -u saboteur &> /dev/null || sudo useradd -m -s /bin/bash saboteur
mkdir -p /var/run/saboteur
chown saboteur:saboteur /var/run/saboteur

mkdir -p /var/log/saboteur
chown saboteur:saboteur /var/log/saboteur
