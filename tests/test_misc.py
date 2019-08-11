# -*- coding: utf-8 -*-

import billboard
import unittest
from nose.tools import raises
from requests.exceptions import ConnectionError
import six


class MiscTest(unittest.TestCase):
    @raises(ConnectionError)
    def testTimeout(self):
        """Checks that using a very small timeout prevents connection."""
        billboard.ChartData("hot-100", timeout=1e-9)

    @raises(billboard.BillboardNotFoundException)
    def testNonExistentChart(self):
        """Checks that requesting a non-existent chart fails."""
        billboard.ChartData("does-not-exist")

    def testUnicode(self):
        """Checks that the Billboard website does not use Unicode characters."""
        chart = billboard.ChartData("hot-100", date="2018-01-27")
        self.assertEqual(
            chart[97].title, six.text_type("El Bano")
        )  # With Unicode this should be "El Baño"

    def testDifficultTitleCasing(self):
        """Checks that a difficult chart title receives proper casing."""
        chart = billboard.ChartData("greatest-r-b-hip-hop-songs")
        self.assertEqual(chart.title, "Greatest of All Time Hot R&B/Hip-Hop Songs")

    def testCharts(self):
        """Checks that the function for listing all charts returns reasonable
        results."""
        charts = billboard.charts()
        self.assertTrue("hot-100" in charts)
        self.assertTrue(200 <= len(charts) <= 400)
