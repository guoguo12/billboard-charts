import unittest
import billboard
import six


class ReprTest(unittest.TestCase):
    """Checks that the string representations of charts and entries are correct.
    """

    @classmethod
    def setUpClass(cls):
        cls.chart = billboard.ChartData("hot-100", date="2010-01-02")

    def testReprChart(self):
        self.assertEqual(
            repr(self.chart), "billboard.ChartData('hot-100', date='2010-01-02')"
        )

    def testReprEntry(self):
        self.assertEqual(
            repr(self.chart[0]),
            "billboard.ChartEntry(title={!r}, artist={!r})".format(
                six.text_type("TiK ToK"), six.text_type("Ke$ha")
            ),
        )
