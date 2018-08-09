import billboard
import unittest
import six


class TestFormatting(unittest.TestCase):
    """Checks consistency of output strings."""

    def test_repr_chart(self):
        chart = billboard.ChartData('hot-100', date='1996-07-30')
        self.assertEqual(repr(chart), "billboard.ChartData('hot-100', date='1996-08-03')")

    def test_repr_entry(self):
        """Checks absense of unicode characters in song titles and artists."""
        chart = billboard.ChartData('latin-pop-songs', date='1994-10-15')
        self.assertEqual(repr(chart[0]),
                         "billboard.ChartEntry(title={!r}, artist={!r})".format(
                             six.text_type('El Dia Que Me Quieras'),
                             six.text_type('Luis Miguel')))
