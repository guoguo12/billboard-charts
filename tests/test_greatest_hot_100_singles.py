import json
import unittest
import billboard


class TestCurrentGreatestHot100Singles(unittest.TestCase):
    """Checks that the ChartData object for the current Greatest Hot 100
    Singles chart has entries and instance variables that are valid and
    reasonable. Does not test whether the data is actually correct.

    The Greatest Hot 100 Singles chart is special in that there are no past
    charts (i.e., there is no historical data).
    """

    def setUp(self):
        self.chart = billboard.ChartData('greatest-hot-100-singles')

    def test_date(self):
        self.assertIsNone(self.chart.date)  # This chart has no dates

    def test_ranks(self):
        ranks = list(entry.rank for entry in self.chart)
        self.assertEqual(ranks, list(range(1, 101)))

    def test_entries_validity(self):
        self.assertEqual(len(self.chart), 100)
        for entry in self.chart:
            self.assertGreater(len(entry.title), 0)
            self.assertGreater(len(entry.artist), 0)
            self.assertIsNone(entry.peakPos)
            self.assertIsNone(entry.lastPos)
            self.assertIsNone(entry.weeks)
            # Redundant because of test_ranks
            self.assertTrue(1 <= entry.rank <= 100)
            self.assertIsInstance(entry.isNew, bool)

    def test_json(self):
        self.assertTrue(json.loads(self.chart.json()))
        for entry in self.chart:
            self.assertTrue(json.loads(entry.json()))
