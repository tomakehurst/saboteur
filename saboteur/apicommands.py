from voluptuous import Schema, All, Required, Optional, Length, Invalid

IPTABLES_COMMAND='sudo /sbin/iptables'
DIRECTIONS={ 'IN': 'INPUT', 'OUT': 'OUTPUT' }
ACTIONS={ 'add': '-A',  'delete': '-D' }

def is_in(value, values):
    if value not in values:
        raise Invalid(value + ' is not one of ' + str(values))
    return True

def OneOf(values):
    return lambda v: is_in(v, values)

class Command:

    def __init__(self, params):
        self.params=params

    def validate(self):
        schema=self.build_schema()
        schema(self.params)

    def execute(self, shell):
        pass

    def build_schema(self):
        combined_schema=dict(BASE_SCHEMA.items() + self.extra_schema().items())
        return Schema(combined_schema)

    def extra_schema(self):
        return {}

    def run_shell_command(self, action, parameters, shell):
        if parameters['type'] == 'FIREWALL_TIMEOUT':
            self.run_firewall_timeout_commands(action, parameters, shell)
        elif parameters['type'] in ['DELAY', 'PACKET_LOSS']:
            self.run_netem_commands(action, parameters, shell)
        else:
            command=self.base_iptables_command(action, parameters, FAULT_TYPES[parameters['type']])
            shell.execute_and_return_status(command)


    def run_firewall_timeout_commands(self, action, parameters, shell):
        allow_conntrack_established_command=self.base_iptables_command(action, parameters, 'ACCEPT') + " -m conntrack --ctstate NEW,ESTABLISHED"
        shell.execute_and_return_status(allow_conntrack_established_command)
        drop_others_command=self.base_iptables_command(action, parameters, 'DROP')
        shell.execute_and_return_status(drop_others_command)
        if action == 'add':
            shell.execute_and_return_status('echo 0 | sudo tee /proc/sys/net/netfilter/nf_conntrack_tcp_loose')
            shell.execute_and_return_status('echo ' + str(parameters['timeout']) + ' | sudo tee /proc/sys/net/netfilter/nf_conntrack_tcp_timeout_established')


    def base_iptables_command(self, action, parameters, fault_type):
        command=IPTABLES_COMMAND + ' ' + ACTIONS[action] + " " + DIRECTIONS[parameters['direction']] + " " + "-p " + (parameters.get('protocol') or "TCP") + " " + "-j " + fault_type

        if parameters.has_key('from'):
            command += ' -s ' + parameters['from']

        if parameters.has_key('to'):
            command += ' -d ' + parameters['to']

        if parameters.has_key('to_port'):
            command += " --dport " + str(parameters['to_port'])

        return command

class NetworkFailure(Command):
    def __init__(self, params):
        Command.__init__(self, params)

    def execute(self, shell):
        command=self.base_iptables_command('add', self.params, 'DROP')
        return shell.execute_and_return_status(command)


class Delay(Command):
    def __init__(self, params):
        Command.__init__(self, params)

    def extra_schema(self):
        return {
            Required('delay'): All(int),
            Optional('distribution'): All(str),
            Optional('correlation'): All(int),
            Optional('variance'): All(int),
            Optional('probability'): All(float)
        }

FAULT_TYPES={ 'NETWORK_FAILURE': NetworkFailure,
              'SERVICE_FAILURE': Command,
              'FIREWALL_TIMEOUT': Command,
              'DELAY': Delay,
              'PACKET_LOSS': Command }


def alphabetical_keys(a_dict):
    keys=a_dict.keys()
    keys.sort()
    return keys

BASE_SCHEMA = {
    Required('name'): All(str, Length(min=1)),
    Required('type'): All(str, OneOf(alphabetical_keys(FAULT_TYPES))),
    Required('direction'): All(str, OneOf(alphabetical_keys(DIRECTIONS))),
    Optional('to'): All(str),
    Optional('to_port'): All(int),
    Optional('protocol'): All(str)
}

def build_command(params):
    if not params.has_key('type') or params['type'] not in FAULT_TYPES.keys():
        message = 'type must be present and one of ' + str(alphabetical_keys(FAULT_TYPES))
        raise Invalid(message, ['type'], message)
    return FAULT_TYPES[params['type']](params)