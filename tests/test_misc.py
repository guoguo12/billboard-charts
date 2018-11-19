# -*- coding: utf-8 -*-

import billboard
import unittest
from nose.tools import raises
from requests.exceptions import ConnectionError
import six


class MiscTest(unittest.TestCase):
    @raises(ConnectionError)
    def test_timeout(self):
        """Checks that using a very small timeout prevents connection."""
        billboard.ChartData('hot-100', timeout=1e-9)

    @raises(billboard.BillboardNotFoundException)
    def test_non_existent_chart(self):
        """Checks that requesting a non-existent chart fails."""
        billboard.ChartData('does-not-exist')

    def test_unicode(self):
        """Checks that the Billboard website does not use Unicode characters."""
        chart = billboard.ChartData('hot-100', date='2018-01-27')
        self.assertEqual(chart[97].title, six.text_type(
            'El Bano'))  # With Unicode this should be "El Baño"
