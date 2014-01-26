#!/usr/bin/env python

import sys
import httplib
import json
from optparse import OptionParser
import os
from os.path import expanduser

BREAKBOX_HOME=expanduser("~") + '/.breakbox'
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
        print(': ' + str(response.status))
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
        print(': ' + str(response.status))
        if response.status != 200:
            print(data)

ACTIONS={'add': add_fault,
    'define-client': define_client,
    'define-service': define_service,
    'reset': reset_hosts
}

if len(sys.argv) < 3:
    print('Usage: ' + sys.argv[0] + ' <action> <client-or-service-name> <OPTIONS>')
    sys.exit(2)

action=sys.argv[1]

if action not in ACTIONS.keys():
    print('Valid actions: ' + ", ".join(ACTIONS.keys()))
    sys.exit(2)

config_name=sys.argv[2]
additional_options=sys.argv[3:]

option_parser=OptionParser()
option_parser.add_option('-t', '--to_port', dest='to_port', type='int')
option_parser.add_option('-f', '--fault_type', dest='type')
option_parser.add_option('-d', '--delay', dest='delay', type='int')
option_parser.add_option('-v', '--variance', dest='variance', type='int')
option_parser.add_option('-c', '--correlation', dest='correlation', type='int')
option_parser.add_option('-i', '--distribution', dest='distribution')
option_parser.add_option('-p', '--protocol', dest='protocol')
option_parser.add_option('-n', '--probability', dest='probability', type='int')
option_parser.add_option('-r', '--from', dest='from')
option_parser.add_option('-o', '--hosts', dest='hosts')

(options, args)=option_parser.parse_args(additional_options)

present_options=dict(filter(lambda (k,v): v is not None, options.__dict__.items()))

action_fn=ACTIONS[action]
action_fn(config_name, present_options)
