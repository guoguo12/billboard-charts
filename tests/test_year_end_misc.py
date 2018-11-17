import billboard
import unittest
from nose.tools import raises
from requests.exceptions import ConnectionError


@raises(ConnectionError)
def test_timeout():
    """Checks that using a very small timeout prevents connection."""
    billboard.YearEnd('hot-100-songs', timeout=1e-9)


@raises(billboard.BillboardNotFoundException)
def test_non_existent_chart():
    """Checks that requesting a non-existent chart fails."""
    billboard.YearEnd('does-not-exist')
