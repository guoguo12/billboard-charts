import json
import os

import billboard
from utils import get_test_dir


class TestCurrentArtist100:
    """Checks that the ChartData object for the current Artist 100 chart
    has all valid fields, and that its entries also have valid fields.

    The Artist 100 chart is special in that it does not provide titles.
    """

    def setUp(self):
        self.chart = billboard.ChartData('artist-100')

    def test_correct_fields(self):
        assert self.chart.date is not None
        assert list(sorted(entry.rank for entry in self.chart)
                    ) == list(range(1, 101))

    def test_valid_entries(self):
        assert len(self.chart) == 100
        for entry in self.chart:
            assert len(entry.title) == 0  # No titles for this chart
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


class TestHistoricalArtist100(TestCurrentArtist100):
    """Checks that the ChartData object for a previous week's Artist 100 chart
    has all valid fields, and that its string representation matches what
    is expected.
    """

    def setUp(self):
        self.chart = billboard.ChartData('artist-100', date='2014-07-26')

    def test_correct_fields(self):
        assert self.chart.date == '2014-07-26'
        assert self.chart.previousDate == '2014-07-19'

    def test_correct_entries(self):
        reference_path = os.path.join(get_test_dir(),
                                      '2014-07-26-artist-100.txt')
        with open(reference_path) as reference:
            assert str(self.chart) == reference.read()
