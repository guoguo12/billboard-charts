import json
import os
import unittest
#import billboard
from utils import get_test_dir

import sys
sys.path.insert(0, '/Users/derrick/Documents/Random Stuff/billboard-charts-master/')
import billboard


class TestCurrentArtist100(unittest.TestCase):
    """Checks that the YearEnd object for the current Top Artists chart has
    entries and instance variables that are valid and reasonable. Does not test
    whether the data is actually correct.

    The Top Artists chart is special in that it does not provide titles.
    """

    def setUp(self):
        self.chart = billboard.YearEnd('top-artists')

    def test_date(self):
        self.assertIsNotNone(self.chart.date)

    def test_ranks(self):
        ranks = list(entry.rank for entry in self.chart)
        self.assertEqual(ranks, list(range(1, 101)))

    def test_entries_validity(self):
        self.assertEqual(len(self.chart), 100)
        for entry in self.chart:
            self.assertEqual(entry.title, '')  # This chart has no titles
            self.assertGreater(len(entry.artist), 0)
            # Redundant because of test_ranks
            self.assertTrue(1 <= entry.rank <= 100)


    def test_json(self):
        self.assertTrue(json.loads(self.chart.json()))
        for entry in self.chart:
            self.assertTrue(json.loads(entry.json()))


class TestHistoricalArtist100(TestCurrentArtist100):
    """Checks that the YearEnd object for a previous and next date. Doesn't
    check if there is a chart.

    Also compares the chart data against a previously downloaded "reference"
    version.
    """

    def setUp(self):
        self.chart = billboard.YearEnd('top-artists')

    def test_date(self):
        self.assertEqual(self.chart.date, 2017)
        self.assertEqual(self.chart.previousDate, '2016')
        self.assertEqual(self.chart.nextDate, '2018')

    def test_entries_correctness(self):
        reference_path = os.path.join(get_test_dir(),
                                      '2017-year-end-top-artist.txt')
        with open(reference_path) as reference:
            self.assertEqual(str(self.chart), reference.read())
