from voluptuous import Schema, All, Any, Required, Optional, Length, MultipleInvalid, Invalid

IPTABLES_COMMAND='sudo /sbin/iptables'
DIRECTIONS={ 'IN': 'INPUT', 'OUT': 'OUTPUT' }
ACTIONS={ 'add': '-A',  'delete': '-D' }

def is_in(value, values):
    if value not in values:
        raise Invalid(value + ' is not one of ' + str(values))
    return True

def OneOf(values):
    return lambda v: is_in(v, values)

string=Any(str, unicode)

def get_network_interface_names(shell):
    exitcode, out, err=shell.execute("netstat -i | tail -n+3 | cut -f1 -d ' '")
    return out.split()

def run_netem_commands2(action, parameters, shell):
    for interface in get_network_interface_names(shell):
        delay_part=netem_delay_part(parameters) if parameters['type'] == 'DELAY' else ''
        packet_loss_part=netem_packet_loss_part(parameters) if parameters['type'] == 'PACKET_LOSS' else ''

        port=str(parameters['to_port'])
        port_type={ 'IN': 'sport', 'OUT': 'dport' }[parameters['direction']]

        shell.execute('sudo /sbin/tc qdisc add dev ' + interface + ' root handle 1: prio')
        shell.execute('sudo /sbin/tc qdisc add dev ' + interface + ' parent 1:3 handle 11:' + delay_part + packet_loss_part)
        shell.execute('sudo /sbin/tc filter add dev ' + interface + ' protocol ip parent 1:0 prio 3 u32 match ip ' + port_type + ' ' + port + ' 0xffff flowid 1:3')

def run_netem_commands(parameters, fault_part, shell):
    for interface in get_network_interface_names(shell):
        port=str(parameters['to_port'])
        port_type={ 'IN': 'sport', 'OUT': 'dport' }[parameters['direction']]

        shell.execute('sudo /sbin/tc qdisc add dev ' + interface + ' root handle 1: prio')
        shell.execute('sudo /sbin/tc qdisc add dev ' + interface + ' parent 1:3 handle 11:' + fault_part)
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


def run_firewall_timeout_commands(action, parameters, shell):
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


class Fault:

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

class ServiceFailure(Fault):
    def __init__(self, params):
        Fault.__init__(self, params)

    def execute(self, shell):
        command=base_iptables_command('add', self.params, 'REJECT --reject-with tcp-reset')
        return shell.execute_and_return_status(command)

class NetworkFailure(Fault):
    def __init__(self, params):
        Fault.__init__(self, params)

    def execute(self, shell):
        command=base_iptables_command('add', self.params, 'DROP')
        return shell.execute_and_return_status(command)


class FirewallTimeout(Fault):
    def __init__(self, params):
        Fault.__init__(self, params)

    def extra_schema(self):
        return {
            Required('timeout'): All(int)
        }

    def execute(self, shell):
        allow_conntrack_established_command=base_iptables_command('add', self.params, 'ACCEPT') + " -m conntrack --ctstate NEW,ESTABLISHED"
        shell.execute_and_return_status(allow_conntrack_established_command)
        drop_others_command=base_iptables_command('add', self.params, 'DROP')
        shell.execute_and_return_status(drop_others_command)
        shell.execute_and_return_status('echo 0 | sudo tee /proc/sys/net/netfilter/nf_conntrack_tcp_loose')
        shell.execute_and_return_status('echo ' + str(self.params['timeout']) + ' | sudo tee /proc/sys/net/netfilter/nf_conntrack_tcp_timeout_established')

class Delay(Fault):
    def __init__(self, params):
        Fault.__init__(self, params)

    def extra_schema(self):
        return {
            Required('delay'): All(int),
            Optional('distribution'): All(string),
            Optional('correlation'): All(int),
            Optional('variance'): All(int),
            Optional('probability'): All(float)
        }

    def execute(self, shell):
        run_netem_commands(self.params, netem_delay_part(self.params), shell)


class PacketLoss(Fault):

    def __init__(self, params):
        Fault.__init__(self, params)

    def extra_schema(self):
        return {
            Optional('probability'): All(float),
            Optional('correlation'): All(int)
        }

    def execute(self, shell):
        run_netem_commands(self.params, netem_packet_loss_part(self.params), shell)


FAULT_TYPES={ 'NETWORK_FAILURE': NetworkFailure,
              'SERVICE_FAILURE': ServiceFailure,
              'FIREWALL_TIMEOUT': FirewallTimeout,
              'DELAY': Delay,
              'PACKET_LOSS': PacketLoss }


def alphabetical_keys(a_dict):
    keys=a_dict.keys()
    keys.sort()
    return keys

BASE_SCHEMA = {
    Required('name'): All(string, Length(min=1)),
    Required('type'): All(string, OneOf(alphabetical_keys(FAULT_TYPES))),
    Required('direction'): All(string, OneOf(alphabetical_keys(DIRECTIONS))),
    Optional('from'): All(string),
    Optional('to'): All(string),
    Optional('to_port'): All(int),
    Optional('protocol'): All(string)
}

def build_command(params):
    if not params.has_key('type') or params['type'] not in FAULT_TYPES.keys():
        message = 'must be present and one of ' + str(alphabetical_keys(FAULT_TYPES))
        exception=MultipleInvalid()
        exception.add(Invalid(message, ['type'], message))
        raise exception
    return FAULT_TYPES[params['type']](params)