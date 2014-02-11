from breakbox import BreakboxWebApp
import json
import unittest

def post_request(params):
    return request('POST', params)
    
def delete_request():
    return { 'path': '/',
             'method': 'DELETE' }

def request(method, params):
    return { 'path': '/',
             'method': method,
             'body': json.dumps(params) }

class TestCommands(unittest.TestCase):
    
    def setUp(self):
        self.shell=MockShell()
        self.app=BreakboxWebApp(self.shell)

    def test_isolate_webserver(self):
        params={ 
            'name': 'isolate-web-server',
            'type': 'NETWORK_FAILURE',
            'direction': 'IN',
            'to_port': 80,
            'protocol': 'TCP'
        }
        response=self.app.handle(post_request(params))
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.last_command, 'sudo /sbin/iptables -A INPUT -p TCP -j DROP --dport 80')
    
    def test_reset(self):
        self.shell.next_result='eth1'
        
        response=self.app.handle(delete_request())
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.commands, [
            'sudo /sbin/iptables -F',
            "netstat -i | tail -n+3 | cut -f1 -d ' '",
            'sudo /sbin/tc qdisc del dev eth1 root'])        
        
    def test_isolate_udp_server(self):
        params={
            'name': "isolate-streaming-server",
            'type': "NETWORK_FAILURE",
            'direction': "IN",
            'to_port': 8111,
            'protocol': "UDP"
        }
        response=self.app.handle(post_request(params))
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.last_command, 'sudo /sbin/iptables -A INPUT -p UDP -j DROP --dport 8111')
        
        
    def test_webserver_shut_down(self):
        params={
            'name': "web-server-down",
            'type': "SERVICE_FAILURE",
            'direction': "IN",
            'to_port': 8080,
            'protocol': "TCP"
        }
        response=self.app.handle(post_request(params))
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.last_command, 'sudo /sbin/iptables -A INPUT -p TCP -j REJECT --dport 8080')
        
        
    def test_client_dependency_unreachable(self):
        params={
            'name': "connectivity-to-dependency-down",
            'type': "NETWORK_FAILURE",
            'direction': "OUT",
            'to': 'my.dest.host.com',
            'to_port': 443,
            'protocol': "TCP"
        }
        response=self.app.handle(post_request(params))
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.last_command, 'sudo /sbin/iptables -A OUTPUT -p TCP -j DROP -d my.dest.host.com --dport 443')
        

    def test_specifying_source(self):
        params={
            'name': "network-failure-by-source-host",
            'type': "NETWORK_FAILURE",
            'direction': "IN",
            'from': 'my.source.host.com',
            'protocol': "TCP"
        }
        response=self.app.handle(post_request(params))
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.last_command, 'sudo /sbin/iptables -A INPUT -p TCP -j DROP -s my.source.host.com')
    
    def test_firewall_timeout(self):
        params={
            'name': "network-failure-by-source-host",
            'type': "FIREWALL_TIMEOUT",
            'direction': "IN",
            'to_port': 3000,
            'protocol': "TCP",
            'timeout': 101
        }
        response=self.app.handle(post_request(params))
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.commands, [
            'sudo /sbin/iptables -A INPUT -p TCP -j ACCEPT --dport 3000 -m conntrack --ctstate NEW,ESTABLISHED',
            'sudo /sbin/iptables -A INPUT -p TCP -j DROP --dport 3000',
            'echo 0 | sudo tee /proc/sys/net/netfilter/nf_conntrack_tcp_loose',
            'echo 101 | sudo tee /proc/sys/net/netfilter/nf_conntrack_tcp_timeout_established'])


    def test_normally_distributed_delay(self):
        params={
            'name': "normally-distributed-delay",
            'type': "DELAY",
            'direction': "IN",
            'to_port': 4411,
            'delay': 160,
            'variance': 12,
            'distribution': 'normal' }
        self.shell.next_result='eth0\nvmnet8'
        response=self.app.handle(post_request(params))
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.commands, [
            "netstat -i | tail -n+3 | cut -f1 -d ' '",
            'sudo /sbin/tc qdisc add dev eth0 root handle 1: prio',
            'sudo /sbin/tc qdisc add dev eth0 parent 1:3 handle 11: netem delay 160ms 12ms distribution normal',
            'sudo /sbin/tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip sport 4411 0xffff flowid 1:3',
            'sudo /sbin/tc qdisc add dev vmnet8 root handle 1: prio',
            'sudo /sbin/tc qdisc add dev vmnet8 parent 1:3 handle 11: netem delay 160ms 12ms distribution normal',
            'sudo /sbin/tc filter add dev vmnet8 protocol ip parent 1:0 prio 3 u32 match ip sport 4411 0xffff flowid 1:3'])

    def test_pareto_distributed_delay(self):
        params={
            'name': "pareto-distributed-delay",
            'type': "DELAY",
            'direction': "IN",
            'to_port': 8822,
            'delay': 350,
            'variance': 50,
            'distribution': 'pareto' }
        self.shell.next_result='eth0'
        response=self.app.handle(post_request(params))
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.commands, [
            "netstat -i | tail -n+3 | cut -f1 -d ' '",
            'sudo /sbin/tc qdisc add dev eth0 root handle 1: prio',
            'sudo /sbin/tc qdisc add dev eth0 parent 1:3 handle 11: netem delay 350ms 50ms distribution pareto',
            'sudo /sbin/tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip sport 8822 0xffff flowid 1:3'])

    def test_uniformly_distributed_delay(self):
        params={
            'name': "uniformly-distributed-delay",
            'type': "DELAY",
            'direction': "IN",
            'to_port': 8822,
            'delay': 120,
            'variance': 5,
            'correlation': 25 }
        self.shell.next_result='eth0'
        response=self.app.handle(post_request(params))
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.commands, [
            "netstat -i | tail -n+3 | cut -f1 -d ' '",
            'sudo /sbin/tc qdisc add dev eth0 root handle 1: prio',
            'sudo /sbin/tc qdisc add dev eth0 parent 1:3 handle 11: netem delay 120ms 5ms 25%',
            'sudo /sbin/tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip sport 8822 0xffff flowid 1:3'])


    def test_outbound_delay(self):
        params={
            'name': "outbound-delay",
            'type': "DELAY",
            'direction': "OUT",
            'to_port': 8822,
            'delay': 350 }
        self.shell.next_result='eth0'
        response=self.app.handle(post_request(params))
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.commands, [
            "netstat -i | tail -n+3 | cut -f1 -d ' '",
            'sudo /sbin/tc qdisc add dev eth0 root handle 1: prio',
            'sudo /sbin/tc qdisc add dev eth0 parent 1:3 handle 11: netem delay 350ms',
            'sudo /sbin/tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip dport 8822 0xffff flowid 1:3'])

    def test_packet_loss(self):
        params={
            'name': "packet-loss",
            'type': "PACKET_LOSS",
            'direction': "IN",
            'to_port': 9191,
            'probability': 0.3 }
        self.shell.next_result='eth0'
        response=self.app.handle(post_request(params))
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.commands, [
            "netstat -i | tail -n+3 | cut -f1 -d ' '",
            'sudo /sbin/tc qdisc add dev eth0 root handle 1: prio',
            'sudo /sbin/tc qdisc add dev eth0 parent 1:3 handle 11: netem loss 0.3%',
            'sudo /sbin/tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip sport 9191 0xffff flowid 1:3'])
    
    def test_packet_loss_with_correlation(self):
        params={
            'name': "packet-loss-with-correlation",
            'type': "PACKET_LOSS",
            'direction': "IN",
            'to_port': 9191,
            'probability': 0.2,
            'correlation': 21 }
        self.shell.next_result='eth0'
        response=self.app.handle(post_request(params))
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.commands, [
            "netstat -i | tail -n+3 | cut -f1 -d ' '",
            'sudo /sbin/tc qdisc add dev eth0 root handle 1: prio',
            'sudo /sbin/tc qdisc add dev eth0 parent 1:3 handle 11: netem loss 0.2% 21%',
            'sudo /sbin/tc filter add dev eth0 protocol ip parent 1:0 prio 3 u32 match ip sport 9191 0xffff flowid 1:3'])

    def test_invalid_input(self):
        params={ 'bad_field': 5 }
        response=self.app.handle(post_request(params))
        response_data=json.loads(response['body'])
        
        self.assertEqual(response['status'], 400)
        self.assertEqual(response_data['message'], "'bad_field' is not a valid parameter")
        

class MockShell:

    def __init__(self, next_status = 0, next_result = "(nothing)"):
        self.next_status = next_status
        self.next_result = next_result
        self.commands=[]

    def execute(self, command):
        self.last_command=command
        self.commands.append(command)
        return 0, self.next_result, ''
        
    def execute_and_return_status(self, command):
        self.commands.append(command)
        self.last_command=command
        return self.next_status

if __name__ == '__main__':
    unittest.main()
