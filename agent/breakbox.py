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
	
def get_established_connection_ports(parameters, shell):
    # ss -no state established '( sport = :8080 or dport = :8080 )'  | tail -n +2 | cut -d ':' -f5 - local ports
	# ss -no state established '( sport = :8080 or dport = :8080 )'  | tail -n +2 | cut -d ':' -f9 - remote ports
	to_port=parameters["to_port"]
	ss_output=shell.execute_and_return_stdout("ss -no state established '( sport = :{0} or dport = :{0} )'".format(to_port))
	lines=ss_output.split('\n')
	lines.pop(0)
	lines.pop(-1)
	return filter(lambda port: port != to_port, [int(line.split(':')[4].strip()) for line in lines] + [int(line.split(':')[8].strip()) for line in lines])
	
class Shell:
	
	def execute_and_return_stdout(self, command):
		return os.popen(command).read()
		
	def execute_and_return_status(self, command):
		return call(command, shell=True)
	
class BreakboxHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	shell=Shell()
	
	def do_POST(self):
		length = int(self.headers.getheader('content-length'))
		params_json=self.rfile.read(length)
		params=json.loads(params_json)
		
		print("Received: " + params_json)
		command=to_shell_command('add', params)
		print("Calling: " + command)
		self.shell.execute_and_return_status(command)
		
		self.send_response(200)
		
		
	def do_DELETE(self):
		command='sudo /sbin/service iptables restart; sudo /sbin/iptables -L'
		print("Calling: " + command)
		self.shell.execute_and_return_status(command)
		
		self.send_response(200)
		
def run_server():
    BaseHTTPServer.test(BreakboxHTTPRequestHandler, BaseHTTPServer.HTTPServer)


if __name__ == '__main__':
    run_server()