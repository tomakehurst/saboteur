import os
import json
import BaseHTTPServer
from subprocess import call

DIRECTIONS={ 'IN': 'INPUT', 'OUT': 'OUTPUT' }
ACTIONS={ 'add': '-A',  'delete': '-D' }
FAULT_TYPES={ "NETWORK_FAILURE": "DROP", "SERVICE_FAILURE": "REJECT" }

def to_shell_command(action, parameters):
	command='iptables ' + ACTIONS[action] + " " + DIRECTIONS[parameters['direction']] + " " + "-p " + parameters['protocol'] + " " + "-j " + FAULT_TYPES[parameters['type']] + " " + "--dport " + str(parameters['to_port'])
	if parameters.has_key('to'):
		command += ' -d ' + parameters['to']
	return command
	
	
class BreakboxHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	
	def do_POST(self):
		length = int(self.headers.getheader('content-length'))
		params_json=self.rfile.read(length)
		params=json.loads(params_json)
		print("Received: " + params_json)
		self.send_response(200)
		self.end_headers()
		self.wfile.write('')
		
def run_server():
    BaseHTTPServer.test(BreakboxHTTPRequestHandler, BaseHTTPServer.HTTPServer)


if __name__ == '__main__':
    run_server()