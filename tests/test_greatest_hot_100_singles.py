import json

import billboard


class TestCurrentGreatestHot100Singles:
    """Checks that the ChartData object for the current Greatest Hot 100
    Singles chart has entries and instance variables that are valid and
    reasonable. Does not test whether the data is actually correct.

    The Greatest Hot 100 Singles chart is special in that there are no past
    charts (i.e., there is no historical data).
    """

    def setUp(self):
        self.chart = billboard.ChartData('greatest-hot-100-singles')

    def test_date(self):
        assert self.chart.date is None  # This chart has no dates

    def test_ranks(self):
        ranks = list(entry.rank for entry in self.chart)
        assert ranks == list(range(1, 101))

    def test_entries_validity(self):
        assert len(self.chart) == 100
        for entry in self.chart:
            assert len(entry.title) > 0
            assert len(entry.artist) > 0
            assert entry.peakPos is None
            assert entry.lastPos is None
            assert entry.weeks is None
            assert 1 <= entry.rank <= 100  # Redundant because of test_ranks
            assert isinstance(entry.isNew, bool)

    def test_json(self):
        assert json.loads(self.chart.json())
