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

    def testYear(self):
        self.assertIsNotNone(self.chart.year)

    def testTitle(self):
        self.assertEqual(self.chart.title, self.expectedTitle)

    def testRanks(self):
        ranks = list(entry.rank for entry in self.chart)
        self.assertEqual(ranks, sorted(ranks))

    def testEntriesValidity(self, skipTitleCheck=False):
        self.assertEqual(len(self.chart), self.expectedNumEntries)
        for entry in self.chart:
            if not skipTitleCheck:
                self.assertGreater(len(entry.title), 0)
            self.assertGreater(len(entry.artist), 0)

    def testJson(self):
        self.assertTrue(json.loads(self.chart.json()))
        for entry in self.chart:
            self.assertTrue(json.loads(entry.json()))


class TestHot100Songs(Base, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = billboard.ChartData("hot-100-songs", year="2019")
        cls.expectedTitle = "Hot 100 Songs - Year-End"
        cls.expectedNumEntries = 100


class TestHotCountrySongs2019(Base, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = billboard.ChartData("hot-country-songs", year="2019")
        cls.expectedTitle = "Hot Country Songs - Year-End"
        cls.expectedNumEntries = 100


class TestHotCountrySongs2010(Base, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = billboard.ChartData("hot-country-songs", year="2010")
        cls.expectedTitle = "Hot Country Songs - Year-End"
        cls.expectedNumEntries = 60


class TestHotCountrySongs1970(Base, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = billboard.ChartData("hot-country-songs", year="1970")
        cls.expectedTitle = "Hot Country Songs - Year-End"
        cls.expectedNumEntries = 34


class TestJazzAlbumsImprints2006(Base, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = billboard.ChartData("jazz-imprints", year="2006")
        cls.expectedTitle = "Jazz Albums Imprints - Year-End"
        cls.expectedNumEntries = 9

    def testEntriesValidity(self):
        super(TestJazzAlbumsImprints2006, self).testEntriesValidity(skipTitleCheck=True)
        for entry in self.chart:
            self.assertEqual(entry.title, "")  # This chart has no titles
