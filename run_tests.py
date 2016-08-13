__doc__ = """This just calls py.test with a couple default arguments.
"""
import pytest
import sys


opts = ['-x', 'App/tests',]


if len(sys.argv) > 1:
    opts.extend(sys.argv[1:])


pytest.main(opts)
