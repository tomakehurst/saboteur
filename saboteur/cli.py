#!/usr/bin/env python

import sys
import httplib
import json
from optparse import OptionParser
import os
from os.path import expanduser

ALL_FAULT_TYPES=['NETWORK_FAILURE', 'SERVICE_FAILURE', 'FIREWALL_TIMEOUT', 'DELAY', 'PACKET_LOSS']
RESPONSES={ 200: 'OK', 400: 'Bad request', 500: 'Server error' }

BREAKBOX_HOME=expanduser("~") + '/.saboteur'
if not os.path.exists(BREAKBOX_HOME):
    os.makedirs(BREAKBOX_HOME)

def load_config(config_name):
    with open(BREAKBOX_HOME + '/' + config_name, 'r') as infile:
        file_contents=infile.read()
        return json.loads(file_contents)

def define_client(config_name, options):
    define_config(config_name, 'client', options)

def define_service(config_name, options):
    define_config(config_name, 'service', options)

def define_config(config_name, type, options):
    direction={ 'service': 'IN', 'client': 'OUT' }[type]
    config={ 'direction': direction, 'to_port': options['to_port'], 'hosts': options['hosts'].split(',') }
    print('Defining config: ' + str(config))
    with open(BREAKBOX_HOME + '/' + config_name, 'w') as outfile:
        json.dump(config, outfile)

def add_fault(config_name, options):
    config=load_config(config_name)
    hosts=config.pop('hosts')
    fault_config=dict(config.items() + options.items())
    print('Adding fault: ' + str(fault_config))
    for host in hosts:
        print('Adding fault to ' + host),
        conn=httplib.HTTPConnection(host, 6660)
        conn.request('POST', '/', json.dumps(fault_config), { 'Content-Type': 'application/json' })
        response=conn.getresponse()
        data=response.read()
        conn.close()
        print(': ' + RESPONSES[response.status])
        if response.status != 200:
            print(data)


def reset_hosts(config_name, options):
    config=load_config(config_name)
    hosts=config.pop('hosts')
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
    'define-client': define_client,
    'define-service': define_service,
    'reset': reset_hosts
}


option_parser=OptionParser(usage="Usage: %prog <action> <client-or-service-name> [options]\n\n\
Valid actions: add, define-client, define-service, reset")
option_parser.add_option('-n', '--name', dest='name', help='A name for the rule', default='(no-name)')
option_parser.add_option('-f', '--from', dest='from', help='Limit rule to packets coming from this host')
option_parser.add_option('-t', '--to', dest='to', help='Limit rule to packets to this host')
option_parser.add_option('-p', '--to_port', dest='to_port', type='int')
option_parser.add_option('-F', '--fault_type', dest='type', help="Valid types: " + ", ".join(ALL_FAULT_TYPES))
option_parser.add_option('-d', '--delay', dest='delay', type='int', help='Delay in milliseconds. Only valid with fault type DELAY.')
option_parser.add_option('-v', '--variance', dest='variance', type='int', help='Delay variance in milliseconds. Only valid with fault type DELAY.')
option_parser.add_option('-c', '--correlation', dest='correlation', type='int', help='Percent delay or packet loss correlation. Only valid with fault type DELAY or PACKET_LOSS.')
option_parser.add_option('-D', '--distribution', dest='distribution', help='Delay distribution type. Valid types: uniform, normal, pareto, paretonormal. Only valid with fault type DELAY.')
option_parser.add_option('-r', '--protocol', dest='protocol', help='Default is TCP')
option_parser.add_option('-P', '--probability', dest='probability', type='int', help='Packet loss probability. Only valid with fault type PACKET_LOSS.')
option_parser.add_option('-T', '--timeout', dest='timeout', type='int', help='TCP connection timeout. Only valid when used with fault type FIREWALL_TIMEOUT.')
option_parser.add_option('-H', '--hosts', dest='hosts', help='Hosts for this client/service')

(options, args)=option_parser.parse_args()

if len(sys.argv) < 2:
    option_parser.print_help()
    sys.exit(2)

action=args[0]
print("action: "+ action)

if action not in ACTIONS.keys():
    print('Valid actions: ' + ", ".join(ACTIONS.keys()))
    sys.exit(2)

config_name=args[1]
print("config_name: " + config_name)
present_options=dict(filter(lambda (k,v): v is not None, options.__dict__.items()))

#print("Action: " + action + ". Options: " + str(options))
action_fn=ACTIONS[action]
action_fn(config_name, present_options)
