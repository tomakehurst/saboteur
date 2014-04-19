#!/usr/bin/env bash

chmod ug+x /usr/lib/saboteur/cli.py /usr/lib/saboteur/agent.py
chown root:root /etc/sudoers.d/saboteur

rm -f /usr/bin/sab
ln -s /usr/lib/saboteur/cli.py /usr/bin/sab

rm -f /usr/bin/saboteur-agent
ln -s /usr/lib/saboteur/agent.py /usr/bin/saboteur-agent

