import json
import os
import unittest

import billboard
from utils import get_test_dir


class CurrentHot100Test(unittest.TestCase):
    """Checks that the ChartData object for the current Hot 100 chart
    has all valid fields, and that its entries also have valid fields.
    """

    def setUp(self):
        self.chart = billboard.ChartData('hot-100')

    def test_correct_fields(self):
        assert self.chart.date is not None
        assert list(sorted(entry.rank for entry in self.chart)
                    ) == list(range(1, 101))

    def test_valid_entries(self):
        assert len(self.chart) == 100
        for entry in self.chart:
            assert len(entry.title) > 0
            assert len(entry.artist) > 0
            assert entry.peakPos >= 1 \
                and entry.peakPos <= 100
            assert entry.lastPos >= 0 \
                and entry.lastPos <= 100  # 0 means new entry
            assert entry.weeks >= 0
            assert entry.rank >= 1 \
                and entry.rank <= 100
            assert repr(entry)

    def test_valid_json(self):
        assert json.loads(self.chart.json())


class HistoricalHot100Test(CurrentHot100Test):
    """Checks that the ChartData object for a previous week's Hot 100 chart
    has all valid fields, and that its string representation matches what
    is expected.
    """

    def setUp(self):
        self.chart = billboard.ChartData('hot-100', date='2015-11-28')

    def test_correct_fields(self):
        assert self.chart.date == '2015-11-28'
        assert self.chart.previousDate == '2015-11-21'

    def test_correct_entries(self):
        reference_path = os.path.join(get_test_dir(), '2015-11-28-hot-100.txt')
        with open(reference_path) as reference:
            assert str(self.chart) == reference.read()
