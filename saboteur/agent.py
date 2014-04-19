#!/usr/bin/env python

import os
import sys
import json
import BaseHTTPServer
from subprocess import Popen, PIPE, call
import logging
from apicommands import build_add_fault_command, build_reset_command
from voluptuous import MultipleInvalid

class ServerError(Exception):
    pass

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

        if exitcode != 0:
            raise ServerError(command + ' exited with ' + str(exitcode))

        return exitcode, out, err
        
class SaboteurWebApp:

    def __init__(self, shell=Shell()):
        self.shell=shell
    
    def handle(self, request):
        if request['method'] == 'POST':
            try:
                params=json.loads(request['body'])
                command=build_add_fault_command(params)
                command.validate()
                command.execute(self.shell)
                response={ 'status': 200, 'body': '{}' }
            except ValueError as ve:
                response={ 'status': 400, 'body': json.dumps('Not valid JSON') }
            except MultipleInvalid as ie:
                response={ 'status': 400, 'body': json.dumps({ 'errors': dict(map(lambda err: [str(err.path[0]), err.error_message], ie.errors))}) }
            except ServerError as se:
                response = { 'status': 500, 'body': json.dumps('Failed to execute a shell command on the server. See the /var/log/saboteur/agent-error.log for details.') }


        elif request['method'] == 'DELETE':
            command=build_reset_command()
            command.execute(self.shell)
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
