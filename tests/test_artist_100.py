import json
import os

import billboard
from utils import get_test_dir


class TestCurrentArtist100:
    """Checks that the ChartData object for the current Artist 100 chart has
    entries and instance variables that are valid and reasonable. Does not test
    whether the data is actually correct.

    The Artist 100 chart is special in that it does not provide titles.
    """

    def setUp(self):
        self.chart = billboard.ChartData('artist-100')

    def test_date(self):
        assert self.chart.date is not None

    def test_ranks(self):
        ranks = list(entry.rank for entry in self.chart)
        assert ranks == list(range(1, 101))

    def test_entries_validity(self):
        assert len(self.chart) == 100
        for entry in self.chart:
            assert entry.title == ''  # This chart has no titles
            assert len(entry.artist) > 0
            assert 1 <= entry.peakPos <= 100
            assert 0 <= entry.lastPos <= 100
            assert entry.weeks >= 0
            assert 1 <= entry.rank <= 100  # Redundant because of test_ranks
            assert isinstance(entry.isNew, bool)

    def test_json(self):
        assert json.loads(self.chart.json())


class TestHistoricalArtist100(TestCurrentArtist100):
    """Checks that the ChartData object for a previous week's Artist 100 chart
    has fields and instance variables that are valid and reasonable.

    Also compares the chart data against a previously downloaded "reference"
    version. This comparison is done based on the string representation; it
    excludes attributes like peakPos and weeks, which can change over time.
    """

    def setUp(self):
        self.chart = billboard.ChartData('artist-100', date='2014-07-26')

    def test_date(self):
        assert self.chart.date == '2014-07-26'
        assert self.chart.previousDate == '2014-07-19'

    def test_entries_correctness(self):
        reference_path = os.path.join(get_test_dir(),
                                      '2014-07-26-artist-100.txt')
        with open(reference_path) as reference:
            assert str(self.chart) == reference.read()
