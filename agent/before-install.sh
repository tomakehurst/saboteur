#!/usr/bin/env bash

[ -f /etc/init.d/saboteur-agent ] && service saboteur-agent stop

id -u saboteur &> /dev/null || useradd -m -s /bin/bash saboteur
mkdir -p /var/run/saboteur
chown saboteur:saboteur /var/run/saboteur

mkdir -p /var/log/saboteur
chown saboteur:saboteur /var/log/saboteur
