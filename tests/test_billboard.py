import json
import os
import re
import unittest

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
        assert list(sorted(entry.rank for entry in self.chart)) == list(range(1, 101))

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


class QuantizeDateTest(unittest.TestCase):
    """Checks that the ChartData object created when the date is invalid
    quantizes to valid date.
    """

    def setUp(self):
        self.chart = billboard.ChartData('hot-100', date='2016-02-12')
        self.chart2 = billboard.ChartData('hot-100', date='2016-02-14')

    def test_correct_entries(self):
        assert len(self.chart) == 100
        assert len(self.chart2) == 100


class VideoLinkTest(unittest.TestCase):
    """Checks that the ChartData object created when the date is invalid
    has no entries.
    """

    def setUp(self):
        self.chart = billboard.ChartData('hot-100', date='2016-07-26')

    def test_correct_entries(self):
        assert self.chart.entries[31].videoLink == 'http://cache.vevo.com/assets/html/embed.html?video=USSM21600522&partnerId=0bcf11f5-81bc-469a-a74f-b370f19def6e&siteSection=billboard_billboard.com'
        assert not self.chart.entries[32].videoLink


def get_test_dir():
    """Returns the name of the directory containing this test file.
    """
    return os.path.dirname(os.path.realpath(__file__))
