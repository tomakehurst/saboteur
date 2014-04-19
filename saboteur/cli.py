#!/usr/bin/env python

import sys
import httplib
import json
from optparse import OptionParser
import os
from os.path import expanduser
from apicommands import FAULT_TYPES

RESPONSES={ 200: 'OK', 400: 'Bad request', 500: 'Server error' }

def add_fault(hosts, options):
    print('Adding fault: ' + json.dumps(options))

    for host in hosts:
        print('Adding fault to ' + host),
        conn=httplib.HTTPConnection(host, 6660)
        conn.request('POST', '/', json.dumps(options), { 'Content-Type': 'application/json' })
        response=conn.getresponse()
        data=response.read()
        conn.close()
        print(': ' + RESPONSES[response.status])
        if response.status != 200:
            print(data)


def reset_hosts(hosts, options):
    for host in hosts:
        print('Resetting host ' + host),
        conn=httplib.HTTPConnection(host, 6660)
        conn.request('DELETE', '/')
        response=conn.getresponse()
        data=response.read()
        conn.close()
        print(': ' + RESPONSES[response.status])
        if response.status != 200:
            print(data)

ACTIONS={'add': add_fault,
         'reset': reset_hosts
}


option_parser=OptionParser(usage="Usage: %prog <action> [options]\n\n\
Valid actions: add, reset")
option_parser.add_option('-n', '--name', dest='name', help='A name for the rule', default='(no-name)')
option_parser.add_option('-f', '--from', dest='from', help='Limit rule to packets coming from this host')
option_parser.add_option('-t', '--to', dest='to', help='Limit rule to packets to this host')
option_parser.add_option('-p', '--to_port', dest='to_port', type='int')
option_parser.add_option('-d', '--direction', dest='direction')
option_parser.add_option('-F', '--fault_type', dest='type', help="Valid types: " + ", ".join(FAULT_TYPES.keys()))
option_parser.add_option('-l', '--delay', dest='delay', type='int', help='Delay in milliseconds. Only valid with fault type DELAY.')
option_parser.add_option('-v', '--variance', dest='variance', type='int', help='Delay variance in milliseconds. Only valid with fault type DELAY.')
option_parser.add_option('-c', '--correlation', dest='correlation', type='int', help='Percent delay or packet loss correlation. Only valid with fault type DELAY or PACKET_LOSS.')
option_parser.add_option('-D', '--distribution', dest='distribution', help='Delay distribution type. Valid types: uniform, normal, pareto, paretonormal. Only valid with fault type DELAY.')
option_parser.add_option('-r', '--protocol', dest='protocol', help='Default is TCP')
option_parser.add_option('-P', '--probability', dest='probability', type='int', help='Packet loss probability. Only valid with fault type PACKET_LOSS.')
option_parser.add_option('-T', '--timeout', dest='timeout', type='int', help='TCP connection timeout. Only valid when used with fault type FIREWALL_TIMEOUT.')
option_parser.add_option('-H', '--hosts', dest='hosts', help='Hosts for this client/service', default='127.0.0.1')

(options, args)=option_parser.parse_args()

if len(sys.argv) < 2:
    option_parser.print_help()
    sys.exit(2)

action=args[0]
print("action: "+ action)

if action not in ACTIONS.keys():
    print('Valid actions: ' + ", ".join(ACTIONS.keys()))
    sys.exit(2)

hosts = options.hosts.split(',')
fault_params = dict(filter(lambda (k,v): k != 'hosts' and v is not None, options.__dict__.items()))

#print("Action: " + action + ". Options: " + str(options))
action_fn=ACTIONS[action]
action_fn(hosts, fault_params)
