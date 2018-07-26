import json
import os
import unittest
import billboard
from utils import get_test_dir


class TestCurrentDigitalAlbums(unittest.TestCase):
    """Checks that the ChartData object for the current Digital Albums chart
    has entries and instance variables that are valid and reasonable. Does not
    test whether the data is actually correct.
    """

    def setUp(self):
        self.chart = billboard.ChartData('digital-albums')

    def test_date(self):
        self.assertIsNotNone(self.chart.date)

    def test_ranks(self):
        ranks = list(entry.rank for entry in self.chart)
        self.assertEqual(ranks, list(range(1, 26)))

    def test_entries_validity(self):
        self.assertEqual(len(self.chart), 25)
        for entry in self.chart:
            self.assertGreater(len(entry.title), 0)
            self.assertGreater(len(entry.artist), 0)
            self.assertTrue(1 <= entry.peakPos <= 100)
            self.assertTrue(0 <= entry.lastPos <= 100)
            self.assertGreaterEqual(entry.weeks, 0)
            # Redundant because of test_ranks
            self.assertTrue(1 <= entry.rank <= 25)
            self.assertIsInstance(entry.isNew, bool)

    def test_entries_consistency(self):
        for entry in self.chart:
            if entry.isNew:
                self.assertEqual(entry.lastPos, 0)

    def test_json(self):
        self.assertTrue(json.loads(self.chart.json()))
        for entry in self.chart:
            self.assertTrue(json.loads(entry.json()))


class TestHistoricalDigitalAlbums(TestCurrentDigitalAlbums):
    """Checks that the ChartData object for a previous week's Digital Albums
    chart has entries and instance variables that are valid and reasonable.

    Also compares the chart data against a previously downloaded "reference"
    version. This comparison is done based on the string representation; it
    excludes attributes like peakPos and weeks, which can change over time.
    """

    def setUp(self):
        self.chart = billboard.ChartData('digital-albums', date='2017-03-04')

    def test_date(self):
        self.assertEqual(self.chart.date, '2017-03-04')
        self.assertEqual(self.chart.previousDate, '2017-02-25')
        self.assertEqual(self.chart.nextDate, '2017-03-11')

    def test_entries_correctness(self):
        reference_path = os.path.join(get_test_dir(),
                                      '2017-03-04-digital-albums.txt')
        with open(reference_path) as reference:
            self.assertEqual(str(self.chart), reference.read())
