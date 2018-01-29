import os

from nose.tools import nottest


@nottest
def get_test_dir():
    """Returns the name of the directory containing this test file.
    """
    return os.path.dirname(os.path.realpath(__file__))
