#!/usr/bin/env sh

sudo id -u breakbox &> /dev/null || sudo useradd -m -s /bin/false breakbox
