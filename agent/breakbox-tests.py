from breakbox import run_shell_command
import unittest


class TestCommandBuilders(unittest.TestCase):

    def setUp(self):
        self.shell=MockShell()
    
    def test_isolate_webserver(self):
        params={ 
            'name': 'isolate-web-server',
            'type': 'NETWORK_FAILURE',
            'direction': 'IN',
            'to_port': 80,
            'protocol': 'TCP'
        }
        run_shell_command('add', params, self.shell)
        self.assertEqual(self.shell.last_command, 'sudo /sbin/iptables -A INPUT -p TCP -j DROP --dport 80')
        

    def test_isolate_webserver_delete(self):
        params={
            'name': "isolate-web-server",
            'type': "NETWORK_FAILURE",
            'direction': "IN",
            'to_port': 81
        }
        run_shell_command('delete', params, self.shell)
        self.assertEqual(self.shell.last_command, 'sudo /sbin/iptables -D INPUT -p TCP -j DROP --dport 81')
        
        
    def test_isolate_udp_server(self):
        params={
            'name': "isolate-streaming-server",
            'type': "NETWORK_FAILURE",
            'direction': "IN",
            'to_port': 8111,
            'protocol': "UDP"
        }
        run_shell_command('add', params, self.shell)
        self.assertEqual(self.shell.last_command, 'sudo /sbin/iptables -A INPUT -p UDP -j DROP --dport 8111')
        
        
    def test_webserver_shut_down(self):
        params={
            'name': "web-server-down",
            'type': "SERVICE_FAILURE",
            'direction': "IN",
            'to_port': 8080,
            'protocol': "TCP"
        }
        run_shell_command('add', params, self.shell)
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
        run_shell_command('add', params, self.shell)
        self.assertEqual(self.shell.last_command, 'sudo /sbin/iptables -A OUTPUT -p TCP -j DROP -d my.dest.host.com --dport 443')
        

    def test_specifying_source(self):
        params={
            'name': "network-failure-by-source-host",
            'type': "NETWORK_FAILURE",
            'direction': "IN",
            'from': 'my.source.host.com',
            'protocol': "TCP"
        }
        run_shell_command('add', params, self.shell)
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
        run_shell_command('add', params, self.shell)
        self.assertEqual(self.shell.commands, [
        	'sudo /sbin/iptables -A INPUT -p TCP -j ACCEPT --dport 3000 -m conntrack --ctstate NEW,ESTABLISHED',
        	'sudo /sbin/iptables -A INPUT -p TCP -j DROP --dport 3000',
        	'echo 0 | sudo tee /proc/sys/net/netfilter/nf_conntrack_tcp_loose',
			'echo 101 | sudo tee /proc/sys/net/netfilter/nf_conntrack_tcp_timeout_established'])
		

class MockShell:

    def __init__(self, next_status = 0, next_result = "(nothing)"):
        self.next_status = next_status
        self.next_result = next_result
        self.commands=[]

    def execute_and_return_stdout(self, command):
        self.last_command=command
        self.commands.append(command)
        return self.next_result
        
    def execute_and_return_status(self, command):
    	self.commands.append(command)
        self.last_command=command
        return self.next_status

if __name__ == '__main__':
    unittest.main()