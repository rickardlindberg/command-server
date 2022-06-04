#!/usr/bin/env python3

import doctest
import subprocess
import sys

class ZeroApp:

    """
    I am a tool to support zero friction development.

    I print usage when called with no arguments:

    >>> ZeroApp.run_in_test_mode(args=[])
    LINE => 'I am a tool to support zero friction development.'
    EXIT => 1

    I run selftest when called with build argument:

    >>> ZeroApp.run_in_test_mode(args=['build'])
    LINE => 'selftest'
    LINE => 'command-server'

    >>> isinstance(ZeroApp(), ZeroApp)
    True
    """

    @staticmethod
    def run_in_test_mode(args=[]):
        events = EventCollector()
        terminal = Terminal.create_null()
        terminal.register_event_listener(events)
        app = ZeroApp(
            args=Args.create_null(args),
            doctest_runner=DoctestRunner.create_null(terminal=terminal),
            terminal=terminal
        )
        try:
            app.run()
        except SystemExit as e:
            events.notify("EXIT", e.code)
        return events

    def __init__(self, args=None, doctest_runner=None, terminal=None):
        self.args = args or Args()
        self.doctest_runner = doctest_runner or DoctestRunner()
        self.terminal = terminal or Terminal()

    def run(self):
        if self.args.get() == ["build"]:
            self.doctest_runner.testmod()
            __import__("command-server")
            self.doctest_runner.testmod(sys.modules["command-server"])
        else:
            self.terminal.print_line("I am a tool to support zero friction development.")
            sys.exit(1)

class EventCollector(list):

    def notify(self, event, message):
        self.append((event, message))

    def __repr__(self):
        return "\n".join(f"{x} => {repr(y)}" for x, y in self)

class Observable:

    def __init__(self):
        self.event_listenters = []

    def register_event_listener(self, listener):
        self.event_listenters.append(listener)

    def notify(self, event, message):
        for listener in self.event_listenters:
            listener.notify(event, message)

class NullStream:

    def write(self, text):
        pass

    def flush(self):
        pass

class Terminal(Observable):

    """
    I represent a terminal to which text can be output.
    """

    @staticmethod
    def create_null():
        return Terminal(NullStream())

    def __init__(self, stdout=sys.stdout):
        Observable.__init__(self)
        self.stdout = stdout

    def print_line(self, text):
        """
        I print a line to stdout:

        >>> subprocess.run([
        ...    "python", "-c",
        ...    "import zero; zero.Terminal().print_line('line')",
        ... ], stdout=subprocess.PIPE).stdout
        b'line\\n'

        I log the printed line.

        >>> events = EventCollector()
        >>> terminal = Terminal.create_null()
        >>> terminal.register_event_listener(events)
        >>> terminal.print_line('hello')
        >>> events
        LINE => 'hello'
        """
        self.notify("LINE", text)
        self.stdout.write(text)
        self.stdout.write("\n")
        self.stdout.flush()

class Args:

    """
    I am an infrastructure wrapper for Python's sys.argv.

    Null version simulates arguments:

    >>> Args.create_null(['hello']).get()
    ['hello']

    Real version gets arguments from Pythons module.

    >>> subprocess.run([
    ...    "python", "-c",
    ...    "import zero; print(zero.Args().get())",
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

class DoctestRunner:

    """
    I am an infrastructure wrapper for Python's doctest module.

    >>> DoctestRunner.create_null(Terminal()).testmod()

    >>> isinstance(DoctestRunner(), DoctestRunner)
    True

    TODO: exit on failure
    TODO: handle return value from testmod
    """

    @staticmethod
    def create_null(terminal):
        return DoctestRunner(doctest=NullDoctest(), terminal=terminal)

    def __init__(self, doctest=doctest, terminal=Terminal()):
        self.doctest = doctest
        self.terminal = terminal

    def testmod(self, module=None):
        if module is None:
            self.terminal.print_line("selftest")
        else:
            self.terminal.print_line("command-server")
        return self.doctest.testmod(module)

class NullSys:

    def __init__(self, argv):
        self.argv = argv

class NullDoctest:

    def testmod(self, m=None):
        pass

if __name__ == "__main__":
    ZeroApp().run()
