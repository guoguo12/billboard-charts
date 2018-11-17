import json
import os
import unittest
import billboard
from utils import get_test_dir


class TestCurrentDigitalAlbums(unittest.TestCase):
    """Checks that the YearEnd object for the current Top Billboard 200 Albums chart
    has entries and instance variables that are valid and reasonable. Does not
    test whether the data is actually correct.
    """

    def setUp(self):
        self.chart = billboard.YearEnd('top-billboard-200-albums')

    def test_date(self):
        self.assertIsNotNone(self.chart.date)

    def test_ranks(self):
        ranks = list(entry.rank for entry in self.chart)
        self.assertEqual(ranks, list(range(1, 201)))

    # chart only has 199 entries
    def test_entries_validity(self):
        self.assertEqual(len(self.chart), 200)
        for entry in self.chart:
            self.assertGreater(len(entry.title), 0)
            self.assertGreater(len(entry.artist), 0)
            # Redundant because of test_ranks
            self.assertTrue(1 <= entry.rank <= 200)

    def test_json(self):
        self.assertTrue(json.loads(self.chart.json()))
        for entry in self.chart:
            self.assertTrue(json.loads(entry.json()))


class TestHistoricalDigitalAlbums(TestCurrentDigitalAlbums):
    """"Checks that the YearEnd object for a previous and next date. Doesn't
    check if there is a chart.

    Also compares the chart data against a previously downloaded "reference"
    version.
    """

    def setUp(self):
        self.chart = billboard.YearEnd('top-billboard-200-albums', date='2015')

    def test_date(self):
        self.assertEqual(self.chart.date, '2015')
        self.assertEqual(self.chart.previousDate, '2014')
        self.assertEqual(self.chart.nextDate, '2016')

    def test_entries_correctness(self):
        reference_path = os.path.join(get_test_dir(),
                                      '2015-year-end-top-billboard-200-albums.txt')
        # Added encoding since in the 2017 chart there is ÷ symbol which messes it up
        with open(reference_path, encoding="utf-8") as reference:
            self.assertEqual(str(self.chart), reference.read())
