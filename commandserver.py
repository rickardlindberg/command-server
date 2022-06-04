"""
A command server runs a command upon startup and repeatedly when told so.

A command client invokes the appropriate command server based on file path.

Step 1: Start server in a directory

    $ cd /foo
    $ command-server echo hello
    hello

The server "registers" in the particular directory, runs the command, and waits
for invocations.

Step 2: Start a client in a subdirectory of a server

    $ cd /foo/bar
    $ command-server --invoke
    ok

The client finds the server registered in /foo and invokes it causing the
server to run the command again.

Step 3: Start a client in a directory without a server registered

    $ cd /baz
    $ command-server --invoke
    no server registered

If the server can listen for changes to files in its directory, it could invoke
itself and remove the need for the client.
"""

import sys
import subprocess

class CommandServerApp:

    """
    >>> arguments = Args.create_null(["echo", "hello"])
    >>> process_factory = ProcessFactory.create_null()
    >>> app = CommandServerApp(arguments, process_factory)

    It runs the command upon startup:

    >>> app.run()
    >>> process_factory.get_last_spawned()
    Process(['echo', 'hello'])

    It runs the command when invoked:

    It can be instantiated without arguments:

    >>> _ = CommandServerApp()
    """

    def __init__(self, arguments=None, process_factory=None):
        self.arguments = arguments or Args()
        self.process_factory = process_factory or ProcessFactory()

    def run(self):
        self.process_factory.spawn(self.arguments.get())

class ProcessFactory:

    """
    Test null version:

    >>> factory = ProcessFactory.create_null()
    >>> factory.get_last_spawned()
    >>> p = factory.spawn(['echo', 'hello'])
    >>> factory.get_last_spawned()
    Process(['echo', 'hello'])
    >>> p is factory.get_last_spawned()
    True
    >>> p.get_pid() is None
    True

    Test real version:

    >>> factory = ProcessFactory()
    >>> process = factory.spawn(['echo', 'hello'])
    >>> isinstance(process.get_pid(), int)
    True
    """

    @staticmethod
    def create_null():
        return ProcessFactory(NullSubprocess())

    def __init__(self, subprocess=subprocess):
        self.last_spwaned = None
        self.subprocess = subprocess

    def spawn(self, command):
        self.last_spwaned = Process(command, self.subprocess.Popen(command))
        return self.last_spwaned

    def get_last_spawned(self):
        return self.last_spwaned

class NullSubprocess:

    def Popen(self, command):
        return NullPopen()

class NullPopen:

    def __init__(self):
        self.pid = None

class Process:

    def __init__(self, command, popen):
        self.command = command
        self.popen = popen

    def get_pid(self):
        return self.popen.pid

    def __repr__(self):
        return f"Process({self.command})"

class Args:

    """
    I am an infrastructure wrapper for Python's sys.argv.

    Null version simulates arguments:

    >>> Args.create_null(['hello']).get()
    ['hello']

    Real version gets arguments from Pythons module.

    >>> subprocess.run([
    ...    "python", "-c",
    ...    "import commandserver; print(commandserver.Args().get())",
    ...    "one", "two",
    ... ], stdout=subprocess.PIPE).stdout
    b"['one', 'two']\\n"
    """

    @staticmethod
    def create_null(args):
        return Args(NullSys(argv=[None]+args))

    def __init__(self, sys=sys):
        self.sys = sys

    def get(self):
        return self.sys.argv[1:]

class NullSys:

    def __init__(self, argv):
        self.argv = argv

if __name__ == "__main__":
    CommandServerApp().run()
