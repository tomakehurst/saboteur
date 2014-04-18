import unittest
from saboteur.apicommands import build_command
from saboteur.voluptuous import Invalid

class TestBase(unittest.TestCase):

    def setUp(self):
        self.shell = MockShell()

    def assertValidAndGeneratesShellCommand(self, params, *expected_shell_commands):
        command = build_command(params)
        command.validate()
        command.execute(self.shell)
        self.assertEqual(self.shell.commands, list(expected_shell_commands))

    def assertValid(self, params):
        command = build_command(params)
        command.validate()

    def assertInvalid(self, params, expected_message):
        try:
            command = build_command(params)
            command.validate()
            raise AssertionError("Expected validation error: " + expected_message)
        except Invalid as e:
            self.assertEquals(expected_message, str(e.path[0]) + ": " + e.error_message)


class TestBasicCommands(TestBase):

    def test_valid_basic_params(self):
        self.assertValid({
            'name': 'do-some-damage',
            'type': 'NETWORK_FAILURE',
            'direction': 'IN',
        })

    def test_invalid_type(self):
        self.assertInvalid({
            'name': 'do-some-damage',
            'type': 'BAD_BALLOON',
            'direction': 'OUT',
        }, "type: type must be present and one of ['DELAY', 'FIREWALL_TIMEOUT', 'NETWORK_FAILURE', 'PACKET_LOSS', 'SERVICE_FAILURE']")

    def test_invalid_direction(self):
        self.assertInvalid({
            'name': 'do-some-damage',
            'type': 'NETWORK_FAILURE',
            'direction': 'SIDEWAYS',
        }, "direction: SIDEWAYS is not one of ['IN', 'OUT']")

class TestServiceFailure(TestBase):

    def test_webserver_shut_down(self):
        params = {
            'name': "web-server-down",
            'type': "SERVICE_FAILURE",
            'direction': "IN",
            'to_port': 8080,
            'protocol': "TCP"
        }
        self.assertValidAndGeneratesShellCommand(params,
            'sudo /sbin/iptables -A INPUT -p TCP -j REJECT --reject-with tcp-reset --dport 8080')


class TestNetworkFailure(TestBase):

    def test_isolate_webserver(self):
        params = {
            'name': 'isolate-web-server',
            'type': 'NETWORK_FAILURE',
            'direction': 'IN',
            'to_port': 80,
            'protocol': 'TCP'
        }

        self.assertValidAndGeneratesShellCommand(params, 'sudo /sbin/iptables -A INPUT -p TCP -j DROP --dport 80')

    def test_isolate_udp_server(self):
        params = {
            'name': "isolate-streaming-server",
            'type': "NETWORK_FAILURE",
            'direction': "IN",
            'to_port': 8111,
            'protocol': "UDP"
        }
        self.assertValidAndGeneratesShellCommand(params, 'sudo /sbin/iptables -A INPUT -p UDP -j DROP --dport 8111')

    def test_client_dependency_unreachable(self):
        params = {
            'name': "connectivity-to-dependency-down",
            'type': "NETWORK_FAILURE",
            'direction': "OUT",
            'to': 'my.dest.host.com',
            'to_port': 443,
            'protocol': "TCP"
        }
        self.assertValidAndGeneratesShellCommand(params, 'sudo /sbin/iptables -A OUTPUT -p TCP -j DROP -d my.dest.host.com --dport 443')

    def test_specifying_source(self):
        params = {
            'name': "network-failure-by-source-host",
            'type': "NETWORK_FAILURE",
            'direction': "IN",
            'from': 'my.source.host.com',
            'protocol': "TCP"
        }
        self.assertValidAndGeneratesShellCommand(params, 'sudo /sbin/iptables -A INPUT -p TCP -j DROP -s my.source.host.com')

class TestFirewallTimeout(TestBase):

    def test_missing_timeout(self):
        self.assertInvalid({
            'name': 'effing-firewalls',
            'type': 'FIREWALL_TIMEOUT',
            'direction': 'IN'
        }, "timeout: required key not provided")

    def test_firewall_timeout(self):
        params = {
            'name': "network-failure-by-source-host",
            'type': "FIREWALL_TIMEOUT",
            'direction': "IN",
            'to_port': 3000,
            'protocol': "TCP",
            'timeout': 101
        }
        self.assertValidAndGeneratesShellCommand(params,
            'sudo /sbin/iptables -A INPUT -p TCP -j ACCEPT --dport 3000 -m conntrack --ctstate NEW,ESTABLISHED',
            'sudo /sbin/iptables -A INPUT -p TCP -j DROP --dport 3000',
            'echo 0 | sudo tee /proc/sys/net/netfilter/nf_conntrack_tcp_loose',
            'echo 101 | sudo tee /proc/sys/net/netfilter/nf_conntrack_tcp_timeout_established')

class TestDelay(TestBase):

    def test_invalid_delay_missing_delay(self):
        self.assertInvalid({
            'name': 'lagtastic',
            'type': 'DELAY',
            'direction': 'IN'
        }, "delay: required key not provided")

    def test_invalid_delay_distribution(self):
        self.assertInvalid({
            'name': 'lagtastic',
            'type': 'DELAY',
            'direction': 'IN',
            'delay': 120,
            'distribution': 1,
        }, "distribution: expected str")

    def test_invalid_delay_correlation(self):
        self.assertInvalid({
            'name': 'lagtastic',
            'type': 'DELAY',
            'direction': 'IN',
            'delay': 120,
            'correlation': 'something',
        }, "correlation: expected int")

    def test_invalid_delay_variance(self):
        self.assertInvalid({
            'name': 'lagtastic',
            'type': 'DELAY',
            'direction': 'IN',
            'delay': 120,
            'variance': 'variable',
        }, "variance: expected int")

    def test_invalid_delay_probability(self):
        self.assertInvalid({
            'name': 'lagtastic',
            'type': 'DELAY',
            'direction': 'IN',
            'delay': 120,
            'probability': 'about half',
        }, "probability: expected float")

    def test_normally_distributed_delay(self):
        params = {
            'name': "normally-distributed-delay",
            'type': "DELAY",
            'direction': "IN",
            'to_port': 4411,
            'delay': 160,
            'variance': 12,
            'distribution': 'normal'}
        self.shell.next_result = 'eth0\nvmnet8'
        self.assertValidAndGeneratesShellCommand(params,
            "netstat -i | tail -n+3 | cut -f1 -d ' '",
            'sudo /sbin/tc qdisc add dev eth0 root handle 1: prio',
            'sudo /sbin/tc qdisc add dev eth0 parent 1:3 handle 11: netem delay 160ms 12ms distribution normal',
            'sudo /sbin/tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip sport 4411 0xffff flowid 1:3',
            'sudo /sbin/tc qdisc add dev vmnet8 root handle 1: prio',
            'sudo /sbin/tc qdisc add dev vmnet8 parent 1:3 handle 11: netem delay 160ms 12ms distribution normal',
            'sudo /sbin/tc filter add dev vmnet8 protocol ip parent 1:0 prio 3 u32 match ip sport 4411 0xffff flowid 1:3')

    def test_pareto_distributed_delay(self):
        params = {
            'name': "pareto-distributed-delay",
            'type': "DELAY",
            'direction': "IN",
            'to_port': 8822,
            'delay': 350,
            'variance': 50,
            'distribution': 'pareto'}
        self.shell.next_result = 'eth0'
        self.assertValidAndGeneratesShellCommand(params,
            "netstat -i | tail -n+3 | cut -f1 -d ' '",
            'sudo /sbin/tc qdisc add dev eth0 root handle 1: prio',
            'sudo /sbin/tc qdisc add dev eth0 parent 1:3 handle 11: netem delay 350ms 50ms distribution pareto',
            'sudo /sbin/tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip sport 8822 0xffff flowid 1:3')

    def test_uniformly_distributed_delay(self):
        params = {
            'name': "uniformly-distributed-delay",
            'type': "DELAY",
            'direction': "IN",
            'to_port': 8822,
            'delay': 120,
            'variance': 5,
            'correlation': 25}
        self.shell.next_result = 'eth0'
        self.assertValidAndGeneratesShellCommand(params,
            "netstat -i | tail -n+3 | cut -f1 -d ' '",
            'sudo /sbin/tc qdisc add dev eth0 root handle 1: prio',
            'sudo /sbin/tc qdisc add dev eth0 parent 1:3 handle 11: netem delay 120ms 5ms 25%',
            'sudo /sbin/tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip sport 8822 0xffff flowid 1:3')


    def test_outbound_delay(self):
        params = {
            'name': "outbound-delay",
            'type': "DELAY",
            'direction': "OUT",
            'to_port': 8822,
            'delay': 350}
        self.shell.next_result = 'eth0'
        self.assertValidAndGeneratesShellCommand(params,
            "netstat -i | tail -n+3 | cut -f1 -d ' '",
            'sudo /sbin/tc qdisc add dev eth0 root handle 1: prio',
            'sudo /sbin/tc qdisc add dev eth0 parent 1:3 handle 11: netem delay 350ms',
            'sudo /sbin/tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dport 8822 0xffff flowid 1:3')


class TestPacketLoss(TestBase):

    def test_invalid_probability(self):
        self.assertInvalid({
            'name': 'scatty',
            'type': 'PACKET_LOSS',
            'direction': 'IN',
            'probability': 'very little',
        }, "probability: expected float")

    def test_invalid_correlation(self):
        self.assertInvalid({
            'name': 'scatty',
            'type': 'PACKET_LOSS',
            'direction': 'IN',
            'correlation': 'what?',
        }, "correlation: expected int")

    def test_packet_loss(self):
        params = {
            'name': "packet-loss",
            'type': "PACKET_LOSS",
            'direction': "IN",
            'to_port': 9191,
            'probability': 0.3}
        self.shell.next_result = 'eth0'
        self.assertValidAndGeneratesShellCommand(params,
            "netstat -i | tail -n+3 | cut -f1 -d ' '",
            'sudo /sbin/tc qdisc add dev eth0 root handle 1: prio',
            'sudo /sbin/tc qdisc add dev eth0 parent 1:3 handle 11: netem loss 0.3%',
            'sudo /sbin/tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip sport 9191 0xffff flowid 1:3')

    def test_packet_loss_with_correlation(self):
        params = {
            'name': "packet-loss-with-correlation",
            'type': "PACKET_LOSS",
            'direction': "IN",
            'to_port': 9191,
            'probability': 0.2,
            'correlation': 21}
        self.shell.next_result = 'eth0'
        self.assertValidAndGeneratesShellCommand(params,
            "netstat -i | tail -n+3 | cut -f1 -d ' '",
            'sudo /sbin/tc qdisc add dev eth0 root handle 1: prio',
            'sudo /sbin/tc qdisc add dev eth0 parent 1:3 handle 11: netem loss 0.2% 21%',
            'sudo /sbin/tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip sport 9191 0xffff flowid 1:3')

class MockShell:
    def __init__(self, next_status=0, next_result="(nothing)"):
        self.next_status = next_status
        self.next_result = next_result
        self.commands = []

    @property
    def last_command(self):
        return self.commands[-1]

    def execute(self, command):
        self.commands.append(command)
        return 0, self.next_result, ''

    def execute_and_return_status(self, command):
        self.commands.append(command)
        return self.next_status


if __name__ == '__main__':
    unittest.main()

