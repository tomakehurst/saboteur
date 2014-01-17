#!/usr/bin/env python

import os
import sys
import json
import BaseHTTPServer
from subprocess import call

class Shell:
    
    def execute_and_return_stdout(self, command):
        print("Calling: " + command)
        return os.popen(command).read()
        
    def execute_and_return_status(self, command):
        print("Calling: " + command)
        return call(command, shell=True)


DIRECTIONS={ 'IN': 'INPUT', 'OUT': 'OUTPUT' }
ACTIONS={ 'add': '-A',  'delete': '-D' }
FAULT_TYPES={ "NETWORK_FAILURE": "DROP", "SERVICE_FAILURE": "REJECT", 'FIREWALL_TIMEOUT': 'DROP' }
IPTABLES_COMMAND='sudo /sbin/iptables'

def run_shell_command(action, parameters, shell=Shell()):
    if parameters['type'] == 'FIREWALL_TIMEOUT':
        run_firewall_timeout_commands(action, parameters, shell)
    elif parameters['type'] == 'DELAY':
        run_netem_commands(action, parameters, shell)
    else:
        command=base_iptables_command(action, parameters, FAULT_TYPES[parameters['type']])
        shell.execute_and_return_status(command)


def run_firewall_timeout_commands(action, parameters, shell=Shell()):
    allow_conntrack_established_command=base_iptables_command(action, parameters, 'ACCEPT') + " -m conntrack --ctstate NEW,ESTABLISHED"
    shell.execute_and_return_status(allow_conntrack_established_command)
    drop_others_command=base_iptables_command(action, parameters, 'DROP')
    shell.execute_and_return_status(drop_others_command)
    if action == 'add':
        shell.execute_and_return_status('echo 0 | sudo tee /proc/sys/net/netfilter/nf_conntrack_tcp_loose')
        shell.execute_and_return_status('echo ' + str(parameters['timeout']) + ' | sudo tee /proc/sys/net/netfilter/nf_conntrack_tcp_timeout_established')
        

def base_iptables_command(action, parameters, fault_type):
    command=IPTABLES_COMMAND + ' ' + ACTIONS[action] + " " + DIRECTIONS[parameters['direction']] + " " + "-p " + (parameters.get('protocol') or "TCP") + " " + "-j " + fault_type
    
    if parameters.has_key('from'):
        command += ' -s ' + parameters['from']
    
    if parameters.has_key('to'):
        command += ' -d ' + parameters['to']
        
    if parameters.has_key('to_port'):
        command += " --dport " + str(parameters['to_port'])
        
    return command  

def get_network_interface_names(shell=Shell()):
    return shell.execute_and_return_stdout("netstat -i | tail -n+3 | cut -f1 -d ' '").split()
    
def run_netem_commands(action, parameters, shell=Shell()):
    for interface in get_network_interface_names(shell):
        delay=str(parameters['delay'])
        variance=str(parameters['variance'])
        distribution=parameters['distribution']
        port=str(parameters['to_port'])
        port_type={ 'IN': 'sport', 'OUT': 'dport' }[parameters['direction']]
        shell.execute_and_return_status('sudo /sbin/tc qdisc add dev ' + interface + ' root handle 1: prio')
        shell.execute_and_return_status('sudo /sbin/tc qdisc add dev ' + interface + ' parent 1:3 handle 11: netem delay ' + delay + 'ms ' + variance + 'ms distribution ' + distribution)
        shell.execute_and_return_status('sudo /sbin/tc filter add dev ' + interface + ' protocol ip parent 1:0 prio 3 u32 match ip ' + port_type + ' ' + port + ' 0xffff flowid 1:3')
        
class BreakboxHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    shell=Shell()
    
    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        params_json=self.rfile.read(length)
        params=json.loads(params_json)
        
        print("Received: " + params_json)
        run_shell_command('add', params)

        self.send_response(200)
        
        
    def do_DELETE(self):
        command=IPTABLES_COMMAND + ' -F'
        self.shell.execute_and_return_status(command)
        
        self.send_response(200)
        
def run_server():
    BaseHTTPServer.test(BreakboxHTTPRequestHandler, BaseHTTPServer.HTTPServer)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.argv.append(6660)
    run_server()