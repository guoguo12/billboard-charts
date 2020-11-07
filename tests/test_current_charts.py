import abc
import json
import six
import unittest
import billboard


@six.add_metaclass(abc.ABCMeta)
class Base:
    @classmethod
    @abc.abstractmethod
    def setUpClass(cls):
        pass

    def testDate(self):
        self.assertIsNotNone(self.chart.date)
        self.assertEqual(self.chart.nextDate, "")

    def testTitle(self):
        self.assertEqual(self.chart.title, self.expectedTitle)

    def testRanks(self):
        ranks = list(entry.rank for entry in self.chart)
        self.assertEqual(ranks, list(range(1, self.expectedNumEntries + 1)))

    def testEntriesValidity(self, skipTitleCheck=False):
        self.assertEqual(len(self.chart), self.expectedNumEntries)
        for entry in self.chart:
            if not skipTitleCheck:
                self.assertGreater(len(entry.title), 0)
            self.assertGreater(len(entry.artist), 0)
            # TODO: Add this check back after we can parse images
            # self.assertGreater(len(entry.image), 0)
            self.assertTrue(1 <= entry.peakPos <= self.expectedNumEntries)
            self.assertTrue(0 <= entry.lastPos <= self.expectedNumEntries)
            self.assertGreaterEqual(entry.weeks, 1)
            self.assertIsInstance(entry.isNew, bool)

    def testEntriesConsistency(self):
        for entry in self.chart:
            if entry.isNew:
                self.assertEqual(0, entry.lastPos)

    def testJson(self):
        self.assertTrue(json.loads(self.chart.json()))
        for entry in self.chart:
            self.assertTrue(json.loads(entry.json()))


class TestCurrentHot100(Base, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = billboard.ChartData("hot-100")
        cls.expectedTitle = "The Hot 100"
        cls.expectedNumEntries = 100


class TestCurrentTraditionalJazzAlbums(Base, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = billboard.ChartData("traditional-jazz-albums")
        cls.expectedTitle = "Traditional Jazz Albums"
        cls.expectedNumEntries = 15


class TestCurrentGreatestHot100Singles(Base, unittest.TestCase):
    """The Greatest Hot 100 Singles chart is special in that there are no past
    charts.
    """

    @classmethod
    def setUpClass(cls):
        cls.chart = billboard.ChartData("greatest-hot-100-singles")
        cls.expectedTitle = "Greatest of All Time Hot 100 Songs"
        cls.expectedNumEntries = 100

    def testDate(self):
        # The date is in fact None
        pass

    def testEntriesValidity(self):
        for entry in self.chart:
            self.assertIsNone(entry.peakPos)
            self.assertIsNone(entry.lastPos)
            self.assertIsNone(entry.weeks)


class TestCurrentArtist100(Base, unittest.TestCase):
    """The Artist 100 chart is special in that it does not have titles.
    """

    @classmethod
    def setUpClass(cls):
        cls.chart = billboard.ChartData("artist-100")
        cls.expectedTitle = "Artist 100"
        cls.expectedNumEntries = 100

    def testEntriesValidity(self):
        super(TestCurrentArtist100, self).testEntriesValidity(skipTitleCheck=True)
        for entry in self.chart:
            self.assertEqual(entry.title, "")  # This chart has no titles
