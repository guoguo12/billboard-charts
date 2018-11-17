import json
import os
import unittest
import billboard
from utils import get_test_dir


# Only has 192 albums since billboard site is missing some 
# (e.g. #36, #44, #55, #57, #78, #81, #135, #154)

class TestCurrentDigitalAlbums(unittest.TestCase):
    """Checks that the YearEnd object for the current Top Billboard 200 Albums chart
    has entries and instance variables that are valid and reasonable. Does not
    test whether the data is actually correct.
    """

    def setUp(self):
        self.chart = billboard.YearEnd('top-billboard-200-albums', date='2002')

    def test_date(self):
        self.assertIsNotNone(self.chart.date)

    def test_ranks(self):
        ranks = list(entry.rank for entry in self.chart)
        # Only has 192 albums since billboard site is missing some
        # n is 201 because list has to go up to 200
        n = 201
        # Added 0 so list starts at 1 like ranks does
        missing_entries = [0, 36, 44, 55, 57, 78, 81, 135, 154]
        x = [i for i in range(n) if i not in missing_entries]
        self.assertEqual(ranks, list(x))

    def test_entries_validity(self):
        self.assertEqual(len(self.chart), 192)
        for entry in self.chart:
            self.assertGreater(len(entry.title), 0)
            self.assertGreater(len(entry.artist), 0)
            # Even though list has 192 entries it does have rank 1 and 200
            self.assertTrue(1 <= entry.rank <= 200)

    def test_json(self):
        self.assertTrue(json.loads(self.chart.json()))
        for entry in self.chart:
            self.assertTrue(json.loads(entry.json()))


class TestHistoricalDigitalAlbums(TestCurrentDigitalAlbums):
    """Checks that the YearEnd object for a previous week's Digital Albums
    chart has entries and instance variables that are valid and reasonable.

    Also compares the chart data against a previously downloaded "reference"
    version. This comparison is done based on the string representation; it
    excludes attributes like peakPos and weeks, which can change over time.
    """

    def setUp(self):
        self.chart = billboard.YearEnd('top-billboard-200-albums', date='2004')

    def test_date(self):
        self.assertEqual(self.chart.date, '2004')
        self.assertEqual(self.chart.previousDate, '2003')
        self.assertEqual(self.chart.nextDate, '2005')

    def test_entries_correctness(self):
        reference_path = os.path.join(get_test_dir(),
                                      '2004-year-end-top-billboard-200-albums.txt')
        with open(reference_path) as reference:
            self.assertEqual(str(self.chart), reference.read())
