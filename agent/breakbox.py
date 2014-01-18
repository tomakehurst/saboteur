#!/usr/bin/env python

import os
import sys
import json
import BaseHTTPServer
from subprocess import Popen, PIPE, call
import logging

class Shell:
    
    def execute(self, command):
        log.info(command)

        proc = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = proc.communicate()
        exitcode = proc.returncode
        
        log.info('[' + str(exitcode) + ']')
        if out:
            log.info(out)

        if err:
            log.info(err)
        
        return exitcode, out, err
        
    def execute_and_return_status(self, command):
        exit_code=call(command, shell=True)
        log.info('"' + command + '" returned ' + str(exit_code))
        return exit_code


DIRECTIONS={ 'IN': 'INPUT', 'OUT': 'OUTPUT' }
ACTIONS={ 'add': '-A',  'delete': '-D' }
FAULT_TYPES={ "NETWORK_FAILURE": "DROP", "SERVICE_FAILURE": "REJECT", 'FIREWALL_TIMEOUT': 'DROP' }
IPTABLES_COMMAND='sudo /sbin/iptables'

def run_shell_command(action, parameters, shell=Shell()):
    if parameters['type'] == 'FIREWALL_TIMEOUT':
        run_firewall_timeout_commands(action, parameters, shell)
    elif parameters['type'] in ['DELAY', 'PACKET_LOSS']:
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
    exitcode, out, err=shell.execute("netstat -i | tail -n+3 | cut -f1 -d ' '")
    return out.split()
    
def run_netem_commands(action, parameters, shell=Shell()):
    for interface in get_network_interface_names(shell):
        delay_part=netem_delay_part(parameters) if parameters['type'] == 'DELAY' else ''
        packet_loss_part=netem_packet_loss_part(parameters) if parameters['type'] == 'PACKET_LOSS' else ''

        port=str(parameters['to_port'])
        port_type={ 'IN': 'sport', 'OUT': 'dport' }[parameters['direction']]    

        shell.execute('sudo /sbin/tc qdisc add dev ' + interface + ' root handle 1: prio')
        shell.execute('sudo /sbin/tc qdisc add dev ' + interface + ' parent 1:3 handle 11:' + delay_part + packet_loss_part)
        shell.execute('sudo /sbin/tc filter add dev ' + interface + ' protocol ip parent 1:0 prio 3 u32 match ip ' + port_type + ' ' + port + ' 0xffff flowid 1:3')

def netem_delay_part(parameters):
    delay=str(parameters['delay'])
    variance_part=' ' + str(parameters['variance']) + 'ms' if parameters.has_key('variance') else ''
    distribution_part=' distribution ' + parameters['distribution'] if parameters.has_key('distribution') else ''              
    correlation_part=' ' + str(parameters['correlation']) + '%' if not parameters.has_key('distribution') and parameters.has_key('correlation') else ''
    return ' netem delay ' + delay + 'ms' + variance_part + distribution_part + correlation_part

def netem_packet_loss_part(parameters):
    probability_part=' ' + str(parameters['probability']) + '%'
    correlation_part=' ' + str(parameters['correlation']) + '%' if parameters.has_key('correlation') else ''
    return ' netem loss' + probability_part + correlation_part
    
def reset_tc(shell=Shell()):
    for interface in get_network_interface_names(shell):
        shell.execute('sudo /sbin/tc qdisc del dev ' + interface + ' root')

class BreakboxHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    shell=Shell()
    
    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        params_json=self.rfile.read(length)
        log.info("Received: " + params_json)
        params=json.loads(params_json)
        
        run_shell_command('add', params)

        self.send_response(200)
        
        
    def do_DELETE(self):
        command=IPTABLES_COMMAND + ' -F'
        self.shell.execute_and_return_status(command)
        reset_tc(self.shell)
        
        self.send_response(200)
        
def run_server():
    BaseHTTPServer.test(BreakboxHTTPRequestHandler, BaseHTTPServer.HTTPServer)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.argv.append(6660)
    
    DEFAULT_LOG_DIR='/var/log/breakbox'
    log_dir=DEFAULT_LOG_DIR if os.path.isdir(DEFAULT_LOG_DIR) else '~/.breakbox'
    logging.basicConfig(filename=log_dir + '/agent.log', level=logging.DEBUG)
    
    global log
    log=logging.getLogger('breakbox-agent')
    ch=logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)
    
    run_server()