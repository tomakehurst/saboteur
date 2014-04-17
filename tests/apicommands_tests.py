import unittest
from saboteur.apicommands import build_command
from saboteur.voluptuous import Invalid

class TestApiCommands(unittest.TestCase):

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

    def test_valid_basic_params(self):
        self.assertValid({
            'name': 'do-some-damage',
            'type': 'FIREWALL_TIMEOUT',
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


    def test_isolate_webserver(self):
        params = {
            'name': 'isolate-web-server',
            'type': 'NETWORK_FAILURE',
            'direction': 'IN',
            'to_port': 80,
            'protocol': 'TCP'
        }

        self.assertValidAndGeneratesShellCommand(params, 'sudo /sbin/iptables -A INPUT -p TCP -j DROP --dport 80')



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

