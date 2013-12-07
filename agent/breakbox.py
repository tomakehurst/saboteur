import os
import json
import BaseHTTPServer
from subprocess import call

DIRECTIONS={ 'IN': 'INPUT', 'OUT': 'OUTPUT' }
ACTIONS={ 'add': '-A',  'delete': '-D' }
FAULT_TYPES={ "NETWORK_FAILURE": "DROP", "SERVICE_FAILURE": "REJECT", 'EXPIRE_ESTABLISHED_CONNECTIONS': 'DROP' }


def to_shell_command(action, parameters):
	command='sudo /sbin/iptables ' + ACTIONS[action] + " " + DIRECTIONS[parameters['direction']] + " " + "-p " + (parameters.get('protocol') or "TCP") + " " + "-j " + FAULT_TYPES[parameters['type']]
	
	if parameters.has_key('from'):
		command += ' -s ' + parameters['from']
	
	if parameters.has_key('to'):
		command += ' -d ' + parameters['to']
		
	if parameters.has_key('to_port'):
		command += " --dport " + str(parameters['to_port'])
		
	if parameters['type'] == 'EXPIRE_ESTABLISHED_CONNECTIONS':
		command += ' -m conntrack --ctstate ESTABLISHED'
		
	return command
	
def get_established_connection_ports(parameters):
    # ss -no state established '( sport = :8080 or dport = :8080 )'  | tail -n +2 | cut -d ':' -f5 - local ports
	# ss -no state established '( sport = :8080 or dport = :8080 )'  | tail -n +2 | cut -d ':' -f9 - remote ports
	return []
	
	
class BreakboxHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	
	def do_POST(self):
		length = int(self.headers.getheader('content-length'))
		params_json=self.rfile.read(length)
		params=json.loads(params_json)
		
		print("Received: " + params_json)
		command=to_shell_command('add', params)
		print("Calling: " + command)
		call(command, shell=True)
		
		self.send_response(200)
		
		
	def do_DELETE(self):
		command='sudo /sbin/service iptables restart; sudo /sbin/iptables -L'
		print("Calling: " + command)
		call(command, shell=True)
		
		self.send_response(200)
		
def run_server():
    BaseHTTPServer.test(BreakboxHTTPRequestHandler, BaseHTTPServer.HTTPServer)


if __name__ == '__main__':
    run_server()