import json
import os
import unittest

import billboard


class CurrentHot100Test(unittest.TestCase):

    def setUp(self):
        self.chart = billboard.ChartData('hot-100')

    def test_correct_fields(self):
        assert self.chart.date is None
        assert self.chart.latest is True

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
        assert json.loads(self.chart.to_JSON())


class HistoricalHot100Test(CurrentHot100Test):

    def setUp(self):
        self.chart = billboard.ChartData('hot-100', date='2015-11-28')

    def test_correct_fields(self):
        assert self.chart.date == '2015-11-28'
        assert self.chart.latest is False

    def test_correct_entries(self):
        reference_path = os.path.join(get_test_dir(), '2015-11-28-output.txt')
        with open(reference_path) as reference:
            assert str(self.chart) == reference.read()


def get_test_dir():
    return os.path.dirname(os.path.realpath(__file__))
