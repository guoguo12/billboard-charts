import json
import os
import unittest
import billboard
from utils import get_test_dir



class TestCurrentHot100(unittest.TestCase):
    """Checks that the YearEnd object for the current (2017) Hot 100 chart has
    entries and instance variables that are valid and reasonable. Does not test
    whether the data is actually correct.
    """

    def setUp(self):
        self.chart = billboard.YearEnd('hot-100-songs')

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
            # Redundant because of test_ranks
            self.assertTrue(1 <= entry.rank <= 100)

    def test_json(self):
        self.assertTrue(json.loads(self.chart.json()))
        for entry in self.chart:
            self.assertTrue(json.loads(entry.json()))


class TestHistoricalHot100(TestCurrentHot100):
    """Checks that the YearEnd object for a previous and next date. Doesn't
    check if there is a chart.

    Also compares the chart data against a previously downloaded "reference"
    version.
    """

    def setUp(self):
        self.chart = billboard.YearEnd('hot-100-songs', date='2015')

    def test_date(self):
        # doesn't have quotes around 2017 since its getting current year
        self.assertEqual(self.chart.date, '2015')
        self.assertEqual(self.chart.previousDate, '2014')
        self.assertEqual(self.chart.nextDate, '2016')

    def test_entries_correctness(self):
        reference_path = os.path.join(get_test_dir(), '2015-year-end-hot-100-songs.txt')
        with open(reference_path) as reference:
            self.assertEqual(str(self.chart), reference.read())
