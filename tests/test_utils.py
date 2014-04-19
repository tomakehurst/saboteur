from saboteur.agent import ServerError

class MockShell:
    def __init__(self, next_exit_code=0, next_result="(nothing)"):
        self.next_exit_code = next_exit_code
        self.next_result = next_result
        self.commands = []

    @property
    def last_command(self):
        return self.commands[-1]

    def execute(self, command):
        self.commands.append(command)
        if self.next_exit_code != 0:
            raise ServerError(command + ' exited with ' + str(self.next_exit_code))
        return self.next_exit_code, self.next_result, ''
