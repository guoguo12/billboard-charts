import unittest
import billboard
import six


class ReprTest(unittest.TestCase):
    def test_repr_chart(self):
        """Checks that the string representation of a chart is correct."""
        chart = billboard.ChartData('hot-100', date='1996-08-03')
        self.assertEqual(repr(chart),
                         "billboard.ChartData('hot-100', date='1996-08-03')")

    def test_repr_entry(self):
        """Checks that the string representation of an entry is correct."""
        chart = billboard.ChartData('hot-100', date='2010-01-02')
        self.assertEqual(repr(chart[0]),
                         'billboard.ChartEntry(title={!r}, artist={!r})'.format(
                             six.text_type('TiK ToK'),
                             six.text_type('Ke$ha')))
