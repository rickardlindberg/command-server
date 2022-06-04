#!/usr/bin/env python3

import doctest
import subprocess
import sys
import unittest

class ZeroApp:

    """
    I am a tool to support zero friction development.

    I print usage when called with no arguments:

    >>> ZeroApp.run_in_test_mode(args=[])
    LINE => 'I am a tool to support zero friction development.'
    EXIT => 1

    I run all tests when called with build argument:

    >>> ZeroApp.run_in_test_mode(args=['build'])
    DOCTEST_MODULE => 'zero'
    DOCTEST_MODULE => 'command-server'
    TEST_RUN => None

    >>> ZeroApp.run_in_test_mode(args=['build'], test_successful=False)
    DOCTEST_MODULE => 'zero'
    DOCTEST_MODULE => 'command-server'
    TEST_RUN => None
    EXIT => 1

    >>> isinstance(ZeroApp(), ZeroApp)
    True
    """

    @staticmethod
    def run_in_test_mode(args=[], test_successful=True):
        events = EventCollector()
        terminal = Terminal.create_null()
        terminal.register_event_listener(events)
        test_runner = TestRunner.create_null(successful=test_successful)
        test_runner.register_event_listener(events)
        app = ZeroApp(
            args=Args.create_null(args),
            test_runner=test_runner,
            terminal=terminal
        )
        try:
            app.run()
        except SystemExit as e:
            events.notify("EXIT", e.code)
        return events

    def __init__(self, args=None, test_runner=None, terminal=None):
        self.args = args or Args()
        self.test_runner = test_runner or TestRunner()
        self.terminal = terminal or Terminal()

    def run(self):
        if self.args.get() == ["build"]:
            self.test_runner.add_doctest_module("zero")
            self.test_runner.add_doctest_module("command-server")
            if not self.test_runner.run():
                sys.exit(1)
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

class TestRunner(Observable):

    """
    I am an infrastructure wrapper for Python's test modules.

    >>> events = EventCollector()
    >>> runner = TestRunner.create_null()
    >>> runner.register_event_listener(events)
    >>> runner.add_doctest_module("zero")
    >>> runner.run()
    True
    >>> events
    DOCTEST_MODULE => 'zero'
    TEST_RUN => None
    """

    @staticmethod
    def create_null(successful=True):
        return TestRunner(unittest=NullUnittest(successful), doctest=NullDoctest())

    def __init__(self, unittest=unittest, doctest=doctest):
        Observable.__init__(self)
        self.unittest = unittest
        self.doctest = doctest
        self.suite = self.unittest.TestSuite()

    def add_doctest_module(self, name):
        self.notify("DOCTEST_MODULE", name)
        self.suite.addTest(self.doctest.DocTestSuite(__import__(name)))

    def run(self):
        self.notify("TEST_RUN", None)
        return self.unittest.TextTestRunner().run(self.suite).wasSuccessful()

class NullSys:

    def __init__(self, argv):
        self.argv = argv

class NullDoctest:

    def DocTestSuite(self, m):
        return unittest.TestSuite()

class NullUnittest:

    def __init__(self, successful):
        self.successful = successful

    def TestSuite(self):
        return unittest.TestSuite()

    def TextTestRunner(self):
        return NullTestRunner(self.successful)

class NullTestRunner:

    def __init__(self, successful):
        self.successful = successful

    def run(self, suite):
        return NullTestResult(self.successful)

class NullTestResult:

    def __init__(self, successful):
        self.successful = successful

    def wasSuccessful(self):
        return self.successful

if __name__ == "__main__":
    ZeroApp().run()
