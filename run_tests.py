__doc__ = """This just calls py.test with a couple default arguments.
    And it serves as a reminder that tests need to be called from this directory.
"""
import pytest
import sys


opts = ['-x', 'Paintings/tests',]


if len(sys.argv) > 1:
    opts.extend(sys.argv[1:])


pytest.main(opts)
