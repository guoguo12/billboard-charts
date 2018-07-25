import json
import os
import unittest
import billboard
from utils import get_test_dir


class TestCurrentHot100(unittest.TestCase):
    """Checks that the ChartData object for the current Hot 100 chart has
    entries and instance variables that are valid and reasonable. Does not test
    whether the data is actually correct.
    """

    def setUp(self):
        self.chart = billboard.ChartData('hot-100')

    def test_date(self):
        self.assertIsNotNone(self.chart.date)

    def test_ranks(self):
        ranks = list(entry.rank for entry in self.chart)
        self.assertEqual(ranks, list(range(1, 101)))

    def test_entries_validity(self):
        self.assertEqual(len(self.chart), 100)
        for entry in self.chart:
            self.assertGreater(len(entry.title), 0)
            self.assertGreater(len(entry.artist), 0)
            self.assertTrue(1 <= entry.peakPos <= 100)
            self.assertTrue(0 <= entry.lastPos <= 100)
            self.assertGreaterEqual(entry.weeks, 0)
            # Redundant because of test_ranks
            self.assertTrue(1 <= entry.rank <= 100)
            self.assertIsInstance(entry.isNew, bool)

    def test_entries_consistency(self):
        for entry in self.chart:
            if entry.isNew:
                self.assertEqual(entry.lastPos, 0)

    def test_json(self):
        self.assertTrue(json.loads(self.chart.json()))
        for entry in self.chart:
            self.assertTrue(json.loads(entry.json()))


class TestHistoricalHot100(TestCurrentHot100):
    """Checks that the ChartData object for a previous week's Hot 100 chart has
    entries and instance variables that are valid and reasonable.

    Also compares the chart data against a previously downloaded "reference"
    version. This comparison is done based on the string representation; it
    excludes attributes like peakPos and weeks, which can change over time.
    """

    def setUp(self):
        self.chart = billboard.ChartData('hot-100', date='2015-11-28')

    def test_date(self):
        self.assertEqual(self.chart.date, '2015-11-28')
        self.assertEqual(self.chart.previousDate, '2015-11-21')
        self.assertEqual(self.chart.nextDate, '2015-12-05')

    def test_entries_correctness(self):
        reference_path = os.path.join(get_test_dir(), '2015-11-28-hot-100.txt')
        with open(reference_path) as reference:
            self.assertEqual(str(self.chart), reference.read())
