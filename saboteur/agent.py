#!/usr/bin/env python

import os
import sys
import json
import BaseHTTPServer
from subprocess import Popen, PIPE, call
import logging
from apicommands import build_command
from voluptuous import Invalid

class ValidationError(Exception):

    def __init__(self, message):
        self.message=message
        
    def __str__(self):
        return self.message

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

ALL_PARAMETER_KEYS=['name', 'type', 'direction', 'from', 'to_port', 'to', 'protocol', 'timeout', 'delay', 'variance', 'correlation', 'distribution', 'probability']
REQUIRED_KEYS=['name', 'type', 'direction']
ALL_FAULT_TYPES=['NETWORK_FAILURE', 'SERVICE_FAILURE', 'FIREWALL_TIMEOUT', 'DELAY', 'PACKET_LOSS']

DIRECTIONS={ 'IN': 'INPUT', 'OUT': 'OUTPUT' }
ACTIONS={ 'add': '-A',  'delete': '-D' }
FAULT_TYPES={ "NETWORK_FAILURE": "DROP", "SERVICE_FAILURE": "REJECT --reject-with tcp-reset", 'FIREWALL_TIMEOUT': 'DROP' }
IPTABLES_COMMAND='sudo /sbin/iptables'

def get_network_interface_names(shell=Shell()):
    exitcode, out, err=shell.execute("netstat -i | tail -n+3 | cut -f1 -d ' '")
    return out.split()

def reset_tc(shell=Shell()):
    for interface in get_network_interface_names(shell):
        shell.execute('sudo /sbin/tc qdisc del dev ' + interface + ' root')

class SaboteurWebApp:

    def __init__(self, shell=Shell()):
        self.shell=shell
    
    def handle(self, request):
        if request['method'] == 'POST':
            params=json.loads(request['body'])
            try:
                command=build_command(params)
                command.validate()
                command.execute(self.shell)
                response={ 'status': 200, 'body': '{}' }
            except ValueError as ve:
                response={ 'status': 400, 'body': json.dumps({ 'message': 'JSON could not be parsed' })}
            except Invalid as ie:
                response={ 'status': 400, 'body': json.dumps({ 'message': str(ie.path[0]) + ': ' + ie.error_message })}


        elif request['method'] == 'DELETE':
            command=IPTABLES_COMMAND + ' -F'
            self.shell.execute_and_return_status(command)
            reset_tc(self.shell)
            response={ 'status': 200 }
        
        return response


class SaboteurHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    app=SaboteurWebApp()
    
    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        body=self.rfile.read(length)
        log.info("Received: " + body)
        
        request={ 'path': self.path, 'method': 'POST', 'body': body }
        response=self.app.handle(request)
        
        self.send_response(response['status'])
        self.end_headers()
        response_body=response['body']
        log.info("Writing response " + response_body)
        self.wfile.write(response_body)
        self.wfile.close()
        
        
    def do_DELETE(self):
        request={ 'path': self.path, 'method': 'DELETE' }
        response=self.app.handle(request)
        self.send_response(response['status'])
        self.end_headers()
        self.wfile.close()
        
        
def run_server():
    BaseHTTPServer.test(SaboteurHTTPRequestHandler, BaseHTTPServer.HTTPServer)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.argv.append(6660)
    
    DEFAULT_LOG_DIR='/var/log/saboteur'
    log_dir=DEFAULT_LOG_DIR if os.path.isdir(DEFAULT_LOG_DIR) else '~/.saboteur'
    logging.basicConfig(filename=log_dir + '/agent.log', level=logging.DEBUG)
    
    global log
    log=logging.getLogger('saboteur-agent')
    ch=logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)
    
    run_server()
