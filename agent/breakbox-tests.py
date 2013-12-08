from breakbox import to_shell_command, get_established_connection_ports
import unittest


class TestCommandBuilders(unittest.TestCase):
	
	def test_isolate_webserver(self):
		params={ 
			'name': 'isolate-web-server',
			'type': 'NETWORK_FAILURE',
			'direction': 'IN',
			'to_port': 80,
			'protocol': 'TCP'
		}
		self.assertEqual(to_shell_command('add', params), 'sudo /sbin/iptables -A INPUT -p TCP -j DROP --dport 80')


	def test_isolate_webserver_delete(self):
		params={
      		'name': "isolate-web-server",
      		'type': "NETWORK_FAILURE",
      		'direction': "IN",
      		'to_port': 81
      	}
		self.assertEqual(to_shell_command('delete', params), 'sudo /sbin/iptables -D INPUT -p TCP -j DROP --dport 81')
		
	def test_isolate_udp_server(self):
		params={
      		'name': "isolate-streaming-server",
      		'type': "NETWORK_FAILURE",
      		'direction': "IN",
      		'to_port': 8111,
      		'protocol': "UDP"
      	}
		self.assertEqual(to_shell_command('add', params), 'sudo /sbin/iptables -A INPUT -p UDP -j DROP --dport 8111')
		
	def test_webserver_shut_down(self):
		params={
      		'name': "web-server-down",
      		'type': "SERVICE_FAILURE",
      		'direction': "IN",
      		'to_port': 8080,
      		'protocol': "TCP"
      	}
		self.assertEqual(to_shell_command('add', params), 'sudo /sbin/iptables -A INPUT -p TCP -j REJECT --dport 8080')
		
	def test_client_dependency_unreachable(self):
		params={
      		'name': "connectivity-to-dependency-down",
      		'type': "NETWORK_FAILURE",
      		'direction': "OUT",
			'to': 'my.dest.host.com',
      		'to_port': 443,
      		'protocol': "TCP"
      	}
		self.assertEqual(to_shell_command('add', params), 'sudo /sbin/iptables -A OUTPUT -p TCP -j DROP -d my.dest.host.com --dport 443')

	def test_specifying_source(self):
		params={
      		'name': "network-failure-by-source-host",
      		'type': "NETWORK_FAILURE",
      		'direction': "IN",
			'from': 'my.source.host.com',
      		'protocol': "TCP"
      	}
		self.assertEqual(to_shell_command('add', params), 'sudo /sbin/iptables -A INPUT -p TCP -j DROP -s my.source.host.com')
	
	example_ss_output="""Recv-Q Send-Q                                            Local Address:Port                                              Peer Address:Port 
0      0                                           ::ffff:192.168.2.11:8080                                       ::ffff:192.168.2.12:52079 
0      0                                           ::ffff:192.168.2.11:8080                                       ::ffff:192.168.2.12:52080 
0      0                                           ::ffff:192.168.2.11:8080                                       ::ffff:192.168.2.12:52078 
"""
	
	def test_emulate_firewall_tcp_expire(self):
		shell=MockShell(next_result=self.example_ss_output)
		params={
			'name': 'firewall-expired-connections',
			'type': 'EXPIRE_ESTABLISHED_CONNECTIONS',
			'direction': 'OUT',
			'to_port': 8080,
			'protocol': 'TCP'
		}
		self.assertEqual(to_shell_command('add', params, shell), 'sudo /sbin/iptables -A OUTPUT -p TCP -j DROP --dport 8080 --match multiport --sports 52079,52080,52078')
		
	def test_correctly_parses_established_ports(self):
		shell=MockShell(next_result=self.example_ss_output)
		params={
			'to_port': 8080
		}
		self.assertEqual(get_established_connection_ports(params, shell), ['52079', '52080', '52078'])


class MockShell:

	def __init__(self, next_status = 0, next_result = "(nothing)"):
		self.next_status = next_status
		self.next_result = next_result

	def execute_and_return_stdout(self, command):
		return self.next_result
		
	def execute_and_return_status(self, command):
		return self.next_status

if __name__ == '__main__':
    unittest.main()