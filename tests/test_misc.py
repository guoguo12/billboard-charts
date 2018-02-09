import billboard
from nose.tools import raises
from requests.exceptions import ConnectionError


@raises(ConnectionError)
def test_timeout():
    """Checks that using a very small timeout prevents connection."""
    billboard.ChartData('hot-100', timeout=1e-9)
