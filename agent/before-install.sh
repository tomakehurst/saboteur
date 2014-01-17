#!/usr/bin/env sh

[ -f /etc/init.d/breakbox-agent ] && service breakbox-agent stop

sudo id -u breakbox &> /dev/null || sudo useradd -m -s /bin/bash breakbox
mkdir -p /var/run/breakbox
chown breakbox:breakbox /var/run/breakbox
