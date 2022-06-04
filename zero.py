#!/usr/bin/env python3

import doctest
import sys

class ZeroApp:

    """
    I am a tool to support zero friction development.

    I print usage if called with no arguments:

    >>> ZeroApp.run_in_test_mode(args=[])
    ('TEXT', 'I am a tool to support zero friction development.\\n')

    I run selftest when called with build argument:

    >>> ZeroApp.run_in_test_mode(args=['build'])
    ('TEXT', 'selftest\\n')
    ('TEXT', 'command-server\\n')

    >>> isinstance(ZeroApp(), ZeroApp)
    True
    """

    @staticmethod
    def run_in_test_mode(args=[]):
        events = Events()
        terminal = Terminal.create_null()
        terminal.listen(events.notify)
        app = ZeroApp(
            args=Args.create_null(args),
            doctest_runner=DoctestRunner.create_null(terminal=terminal),
            terminal=terminal
        )
        app.run()
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
            self.terminal.write("I am a tool to support zero friction development.")

class Events(list):

    def notify(self, type, text):
        self.append((type, text))

    def __repr__(self):
        return "\n".join(repr(x) for x in self)

class Observable:

    def __init__(self):
        self.event_listenters = []

    def listen(self, listener):
        self.event_listenters.append(listener)

    def notify(self, type, event):
        for notify in self.event_listenters:
            notify(type, event)

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

    def write(self, text):
        """
        I log the text written.

        >>> events = Events()
        >>> terminal = Terminal.create_null()
        >>> terminal.listen(events.notify)
        >>> terminal.write('hello')
        >>> events
        ('TEXT', 'hello\\n')
        """
        x = f"{text}\n"
        self.notify("TEXT", x)
        self.stdout.write(x)
        self.stdout.flush()

class Args:

    """
    I am an infrastructure wrapper for Python's sys.argv.

    Null version simulates arguments:

    >>> Args.create_null(['hello']).get()
    ['hello']

    Real version gets arguments from Pythons module.

    >>> Args().get() == sys.argv[1:]
    True
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
            self.terminal.write("selftest")
        else:
            self.terminal.write("command-server")
        return self.doctest.testmod(module)

class NullSys:

    def __init__(self, argv):
        self.argv = argv

class NullDoctest:

    def testmod(self, m=None):
        pass

if __name__ == "__main__":
    ZeroApp().run()
