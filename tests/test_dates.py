import datetime
import json
import unittest

import billboard


class DateRoundingTest(unittest.TestCase):
    """Checks that the Billboard website is rounding dates correctly: it should
    round up to the nearest date on which a chart was published.
    """

    def setUp(self):
        self.chart = billboard.ChartData('hot-100', date='1000-10-10')

    def test_correct_fields(self):
        assert self.chart.date == '1958-08-04'  # The first Hot 100 chart


class DatetimeTest(unittest.TestCase):
    """Checks that ChartData correctly handles datetime objects as the
    date parameter.
    """

    def setUp(self):
        self.chart = billboard.ChartData('hot-100', datetime.date(2016, 7, 8))

    def test_successful_load(self):
        self.assertTrue(len(self.chart) > 0)
