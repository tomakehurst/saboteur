#!/usr/bin/env sh

sudo id -u breakbox &> /dev/null || sudo useradd -m -s /bin/false breakbox
mkdir -p /var/run/breakbox
chown breakbox:breakbox /var/run/breakbox
