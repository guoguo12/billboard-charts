import abc
import json
import unittest
import warnings

import billboard
import six
from billboard import UnsupportedYearWarning


@six.add_metaclass(abc.ABCMeta)
class Base:
    @classmethod
    @abc.abstractmethod
    def setUpClass(cls):
        pass

    def testYear(self):
        self.assertIsNotNone(self.chart.year)

    def testNextYear(self):
        next_year = str(int(self.chart.year) + 1)
        self.assertEqual(self.chart.nextYear, next_year)

    def testPreviousYear(self):
        previous_year = str(int(self.chart.year) - 1)
        self.assertEqual(self.chart.previousYear, previous_year)

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


class TestHot100Songs2019(Base, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = billboard.ChartData("hot-100-songs", year="2019")
        cls.expectedTitle = "Hot 100 Songs - Year-End"
        cls.expectedNumEntries = 100

    def testNextYear(self):
        self.assertIsNone(self.chart.nextYear)


class TestHotCountrySongs1970(Base, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name = "hot-country-songs"
        year = 1970
        warnings.filterwarnings(action="always", category=UnsupportedYearWarning)
        with warnings.catch_warnings(record=True) as w:
            cls.chart = billboard.ChartData(name, year=year)
            cls.warning = w[0] if w else None

        cls.expectedTitle = "Hot Country Songs - Year-End"
        cls.expectedNumEntries = 34

    def testUnsupportedYearWarning(self):
        self.assertEquals(self.warning.category, UnsupportedYearWarning)

    def testNextYear(self):
        self.assertIsNone(self.chart.nextYear)

    def testPreviousYear(self):
        self.assertIsNone(self.chart.previousYear)


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

    def testPreviousYear(self):
        self.assertIsNone(self.chart.previousYear)
