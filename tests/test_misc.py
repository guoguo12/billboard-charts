import billboard
import unittest
import six
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

    def test_unicode(self):
        """Checks that the Billboard website does not use Unicode characters."""
        chart = billboard.ChartData('latin-pop-songs', date='1994-10-15')
        self.assertEqual(chart[0].title, six.text_type(
            'El Dia Que Me Quieras'))
        self.assertEqual(chart[0].artist, six.text_type('Luis Miguel'))
