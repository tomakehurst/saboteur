from saboteur.agent import SaboteurWebApp
import json
import unittest
from test_utils import MockShell
from saboteur.apicommands import FAULT_TYPES, alphabetical_keys


def post_request(params):
    return request('POST', params)


def delete_request():
    return {'path': '/',
            'method': 'DELETE'}


def request(method, params):
    return {'path': '/',
            'method': method,
            'body': json.dumps(params)}


def http_request(method, params_json):
    return {'path': '/',
            'method': method,
            'body': params_json}


class TestAgent(unittest.TestCase):
    def setUp(self):
        self.shell = MockShell()
        self.app = SaboteurWebApp(self.shell)

    def test_successful_iptables_based_fault_returns_200_and_executes_correct_command(self):
        params = json.dumps({
            'name': 'isolate-web-server',
            'type': 'NETWORK_FAILURE',
            'direction': 'IN',
            'to_port': 80,
            'protocol': 'TCP'
        })
        response = self.app.handle(http_request('POST', params))
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.last_command, 'sudo /sbin/iptables -A INPUT -p TCP -j DROP --dport 80')

    def test_invalid_json_returns_400(self):
        params = '{ "name": }'
        response = self.app.handle(http_request('POST', params))
        self.assertEqual(400, response['status'])
        self.assertEqual(json.dumps('Not valid JSON'), response['body'])

    def test_invalid_fault_type(self):
        params = json.dumps({
            'name': 'isolate-web-server',
            'type': 'WORMS'
        })
        response = self.app.handle(http_request('POST', params))
        self.assertEqual(400, response['status'])
        self.assertEqual(json.dumps({
            "errors": {
                "type": "must be present and one of " + str(alphabetical_keys(FAULT_TYPES))
            }
        }),
                         response['body'])

    def test_fault_with_single_invalid_field_returns_400(self):
        params = json.dumps({
            'name': 'isolate-web-server',
            'type': 'NETWORK_FAILURE',
            'to_port': 7871
        })
        response = self.app.handle(http_request('POST', params))
        self.assertEqual(400, response['status'])
        self.assertEqual(json.dumps({
            "errors": {
                "direction": "required key not provided"
            }
        }),
                         response['body'])

    def test_fault_with_multiple_invalid_fields_returns_400(self):
        params = json.dumps({
            'name': 'isolate-web-server',
            'type': 'DELAY',
            'direction': 'IN',
            'to_port': 7871,
            'delay': 'bad',
            'probability': 'worse'
        })
        response = self.app.handle(http_request('POST', params))
        self.assertEqual(400, response['status'])
        self.assertEqual(json.dumps({
            "errors": {
                "delay": "expected int",
                "probability": "expected float"
            }
        }),
                         response['body'])

    def test_reset(self):
        self.shell.next_result = 'eth1'

        response = self.app.handle(delete_request())
        self.assertEqual(response['status'], 200)
        self.assertEqual(self.shell.commands, [
            'sudo /sbin/iptables -F',
            "netstat -i | tail -n+3 | cut -f1 -d ' '",
            'sudo /sbin/tc qdisc del dev eth1 root'])

    def test_returns_500_when_shell_command_exits_with_non_zero(self):
        params = json.dumps({
            'name': 'whatever',
            'type': 'NETWORK_FAILURE',
            'direction': 'IN',
            'to_port': 80,
            'protocol': 'TCP'
        })

        self.shell.next_exit_code = 1
        response = self.app.handle(http_request('POST', params))
        self.assertEqual(500, response['status'])


if __name__ == '__main__':
    unittest.main()
