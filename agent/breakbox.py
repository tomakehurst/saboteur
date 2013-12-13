import os
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
    else:
        command=base_iptables_command(action, parameters, FAULT_TYPES[parameters['type']])
        shell.execute_and_return_status(command)


def run_firewall_timeout_commands(action, parameters, shell=Shell()):
    allow_conntrack_established_command=base_iptables_command(action, parameters, 'ACCEPT') + " -m conntrack --ctstate NEW,ESTABLISHED"
    shell.execute_and_return_status(allow_conntrack_established_command)
    drop_others_command=base_iptables_command(action, parameters, 'DROP')
    shell.execute_and_return_status(drop_others_command)
    if action == 'add':
    	shell.execute_and_return_status('echo 0 > /proc/sys/net/netfilter/nf_conntrack_tcp_loose')
        shell.execute_and_return_status('echo ' + str(parameters['timeout']) + ' > /proc/sys/net/netfilter/nf_conntrack_tcp_timeout_established')
        

def base_iptables_command(action, parameters, fault_type):
    command=IPTABLES_COMMAND + ' ' + ACTIONS[action] + " " + DIRECTIONS[parameters['direction']] + " " + "-p " + (parameters.get('protocol') or "TCP") + " " + "-j " + fault_type
    
    if parameters.has_key('from'):
        command += ' -s ' + parameters['from']
    
    if parameters.has_key('to'):
        command += ' -d ' + parameters['to']
        
    if parameters.has_key('to_port'):
        command += " --dport " + str(parameters['to_port'])
        
    return command  

    
        
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
        command='sudo /sbin/iptables -F'
        self.shell.execute_and_return_status(command)
        
        self.send_response(200)
        
def run_server():
    BaseHTTPServer.test(BreakboxHTTPRequestHandler, BaseHTTPServer.HTTPServer)


if __name__ == '__main__':
    run_server()