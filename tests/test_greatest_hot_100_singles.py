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

    def test_title(self):
        self.assertEqual(self.chart.title,
                         'Greatest of All Time Hot 100 Singles')

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
            self.assertGreater(len(entry.image), 0)
            self.assertIsNone(entry.peakPos)
            self.assertEqual(entry.lastPos, 0)
            self.assertEqual(entry.weeks, 1)  # This is kind of unintuitive...
            # Redundant because of test_ranks
            self.assertTrue(1 <= entry.rank <= 100)
            self.assertIsInstance(entry.isNew, bool)

    def test_json(self):
        self.assertTrue(json.loads(self.chart.json()))
        for entry in self.chart:
            self.assertTrue(json.loads(entry.json()))
