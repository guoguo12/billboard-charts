import billboard
import unittest
from nose.tools import raises
from requests.exceptions import ConnectionError, ReadTimeout


class MiscTests(unittest.TestCase):
    @raises(ConnectionError, ReadTimeout)
    def test_timeout(self):
        """Checks that using a very small timeout prevents connection."""
        billboard.ChartData('hot-100', timeout=1e-9)


    @raises(billboard.BillboardNotFoundException)
    def test_non_existent_chart(self):
        """Checks that requesting a non-existent chart fails."""
        billboard.ChartData('does-not-exist')
