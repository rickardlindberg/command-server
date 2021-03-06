#!/usr/bin/env python3

import doctest
import subprocess
import sys
import unittest

from commandserver import Args

class ZeroApp:

    """
    I am a tool to support zero friction development.

    ## Usage

    I print usage when called with no arguments:

    >>> ZeroApp.run_in_test_mode(args=[])
    LINE => 'I am a tool to support zero friction development.'
    EXIT => 1

    ## Building

    I run all tests when called with build argument:

    >>> ZeroApp.run_in_test_mode(args=['build'])
    DOCTEST_MODULE => 'zero'
    DOCTEST_MODULE => 'commandserver'
    TEST_RUN => None

    I exit with status of 1 if there are test failures:

    >>> ZeroApp.run_in_test_mode(
    ...     args=['build'], test_successful=False
    ... ).filter(["EXIT"])
    EXIT => 1
    """

    def __init__(self, args=None, test_runner=None, terminal=None):
        self.args = args or Args()
        self.test_runner = test_runner or TestRunner()
        self.terminal = terminal or Terminal()

    def run(self):
        if self.args.get() == ["build"]:
            self.test_runner.add_doctest_module("zero")
            self.test_runner.add_doctest_module("commandserver")
            if not self.test_runner.run():
                sys.exit(1)
        else:
            self.terminal.print_line("I am a tool to support zero friction development.")
            sys.exit(1)

    @staticmethod
    def run_in_test_mode(args=[], test_successful=True):
        events = EventCollector()
        terminal = Terminal.create_null()
        terminal.register_event_listener(events)
        test_runner = TestRunner.create_null(run_was_successful=test_successful)
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

class EventCollector(list):

    def notify(self, event, message):
        self.append((event, message))

    def filter(self, events):
        filtered = EventCollector()
        for x in self:
            if x[0] in events:
                filtered.append(x)
        return filtered

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

class Terminal(Observable):

    """
    I represent a terminal to which text can be output.
    """

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

    @staticmethod
    def create_null():
        class NullStream:
            def write(self, text):
                pass
            def flush(self):
                pass
        return Terminal(NullStream())

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

    @staticmethod
    def create_null(run_was_successful=True):
        class NullUnittest:
            def TestSuite(self):
                return NullTestSuite()
            def TextTestRunner(self):
                return NullTestRunner()
        class NullTestRunner:
            def run(self, suite):
                return NullTestResult()
        class NullTestResult:
            def wasSuccessful(self):
                return run_was_successful
        class NullDoctest:
            def DocTestSuite(self, m):
                return NullTestSuite()
        class NullTestSuite:
            def addTest(self, test):
                pass
        return TestRunner(
            unittest=NullUnittest(),
            doctest=NullDoctest()
        )

if __name__ == "__main__":
    ZeroApp().run()
