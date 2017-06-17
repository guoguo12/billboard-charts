from itertools import chain, repeat
import json
import os
import re
import unittest
import datetime

import billboard

VALID_CHANGE_REGEX = r'^(\+\d{1,2}|\-\d{1,2}|0|Hot Shot Debut|New|Re-Entry)$'


class CurrentHot100Test(unittest.TestCase):
    """Checks that the ChartData object for the current Hot 100 chart
    has all valid fields, and that its entries also have valid fields.
    """

    def setUp(self):
        self.chart = billboard.ChartData('hot-100')

    def test_correct_fields(self):
        assert self.chart.date is not None
        assert self.chart.latest is True
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
            assert re.match(VALID_CHANGE_REGEX, entry.change)
            assert entry.spotifyID is not None
            assert entry.spotifyLink == '' \
                or 'embed.spotify.com' in entry.spotifyLink
            assert repr(entry)

    def test_valid_json(self):
        assert json.loads(self.chart.to_JSON())


class HistoricalHot100Test(CurrentHot100Test):
    """Checks that the ChartData object for a previous week's Hot 100 chart
    has all valid fields, and that its string representation matches what
    is expected.
    """

    def setUp(self):
        self.chart = billboard.ChartData('hot-100', date='2015-11-28')

    def test_correct_fields(self):
        assert self.chart.date == '2015-11-28'
        assert self.chart.latest is False
        assert self.chart.previousDate == '2015-11-21'

    def test_correct_entries(self):
        reference_path = os.path.join(get_test_dir(), '2015-11-28-output.txt')
        with open(reference_path) as reference:
            assert str(self.chart) == reference.read()


class Hot100QuantizationTest(unittest.TestCase):
    """Checks that the date quantization feature for ChartData
    functions correctly.
    """

    def setUp(self):
        dates = ['2016-07-0%d' % x for x in range(1, 8)]  # 7/1/16 to 7/7/16
        self.charts = [billboard.ChartData(
            'hot-100', date=date, fetch=False) for date in dates]

    def test_correct_fields(self):
        dates = [chart.date for chart in self.charts]
        reference_dates = list(
            chain(repeat('2016-07-02', 2), repeat('2016-07-09', 5)))
        assert dates == reference_dates


class DatetimeTest(unittest.TestCase):
    """Checks that ChartData correctly handles datetime objects as the
    date parameter.
    """

    def setUp(self):
        self.chart = billboard.ChartData('hot-100', datetime.date(2016, 7, 8))

    def test_successful_load(self):
        self.assertTrue(len(self.chart) > 0)


class InvalidDateTest(unittest.TestCase):
    """Checks that the ChartData object created when the date is
    invalid (and quantization is turned off) has no entries.
    """

    def setUp(self):
        self.chart = billboard.ChartData(
            'hot-100', date='2016-02-12', quantize=False)

    def test_correct_entries(self):
        assert len(self.chart) == 0


def get_test_dir():
    """Returns the name of the directory containing this test file.
    """
    return os.path.dirname(os.path.realpath(__file__))
