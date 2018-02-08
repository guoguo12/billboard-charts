import json

import billboard


class TestCurrentGreatestHot100Singles:
    """Checks that the ChartData object for the current Greatest Hot 100
    Singles chart has all valid fields, and that its entries also have valid
    fields.

    The Greatest Hot 100 Singles chart is special in that it does not provide
    peak/last position or weeks-on-chart data.
    """

    def setUp(self):
        self.chart = billboard.ChartData('greatest-hot-100-singles')

    def test_correct_fields(self):
        assert self.chart.date is None
        assert list(sorted(entry.rank for entry in self.chart)
                    ) == list(range(1, 101))

    def test_valid_entries(self):
        assert len(self.chart) == 100
        for entry in self.chart:
            assert len(entry.title) > 0
            assert len(entry.artist) > 0
            assert entry.peakPos is None
            assert entry.lastPos is None
            assert entry.weeks is None
            assert entry.rank >= 1 \
                and entry.rank <= 100
            assert repr(entry)

    def test_valid_json(self):
        assert json.loads(self.chart.json())
