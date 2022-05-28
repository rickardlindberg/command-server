#!/usr/bin/env python3

import doctest
import sys

class ZeroApp:

    """
    I print usage if called with no arguments:

    >>> ZeroApp.create_null().run()
    I am a tool to support zero friction development.

    I run selftest when called with build argument:

    >>> ZeroApp.create_null(args=['build']).run()
    selftest
    command-server

    TODO: build
        compile and/or lint, run tests, and report success or failure

    TODO: watch
        automatically run build when files change

    TODO: integrate
        run build in a production-like environment and integrate your code

    TODO: deploy
        runt integrate, then deploy the integration branch

    TODO: rundev
        run the software locally for manual review and testing

    >>> isinstance(ZeroApp(), ZeroApp)
    True
    """

    @staticmethod
    def create_null(args=[]):
        return ZeroApp(
            args=Args.create_null(args),
            doctest_runner=DoctestRunner.create_null()
        )

    def __init__(self, args=None, doctest_runner=None):
        self.args = args or Args()
        self.doctest_runner = doctest_runner or DoctestRunner()

    def run(self):
        if self.args.get() == ["build"]:
            self.doctest_runner.testmod()
            __import__("command-server")
            self.doctest_runner.testmod(sys.modules["command-server"])
        else:
            print("I am a tool to support zero friction development.")

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

    >>> DoctestRunner.create_null().testmod()
    selftest

    >>> isinstance(DoctestRunner(), DoctestRunner)
    True

    TODO: exit on failure
    TODO: handle return value from testmod
    """

    @staticmethod
    def create_null():
        return DoctestRunner(doctest=NullDoctest())

    def __init__(self, doctest=doctest):
        self.doctest = doctest

    def testmod(self, module=None):
        if module is None:
            print("selftest")
        else:
            print("command-server")
        return self.doctest.testmod(module)

class NullSys:

    def __init__(self, argv):
        self.argv = argv

class NullDoctest:

    def testmod(self, m=None):
        pass

if __name__ == "__main__":
    ZeroApp().run()
