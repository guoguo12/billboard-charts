import abc
import json
import os
import six
import unittest
import billboard


@six.add_metaclass(abc.ABCMeta)
class Base:
    @classmethod
    @abc.abstractmethod
    def setUpClass(cls):
        pass

    def testCorrectnessVersusReference(self):
        testDir = os.path.dirname(os.path.realpath(__file__))
        referencePath = os.path.join(testDir, self.referenceFile)
        with open(referencePath) as reference:
            reference = json.loads(reference.read())

        self.assertEqual(self.chart.name, reference["name"])
        self.assertEqual(self.chart.title, reference["title"])
        self.assertEqual(self.chart.date, reference["date"])
        self.assertEqual(self.chart.previousDate, reference["previousDate"])
        self.assertEqual(self.chart.nextDate, reference["nextDate"])

        self.assertEqual(len(self.chart.entries), len(reference["entries"]))
        for chartEntry, referenceEntry in zip(self.chart.entries, reference["entries"]):
            # We intentionally don't check image here, since image URLs might
            # change a lot
            self.assertEqual(chartEntry.title, referenceEntry["title"])
            self.assertEqual(chartEntry.artist, referenceEntry["artist"])
            self.assertEqual(chartEntry.peakPos, referenceEntry["peakPos"])
            self.assertEqual(chartEntry.lastPos, referenceEntry["lastPos"])
            self.assertEqual(chartEntry.weeks, referenceEntry["weeks"])
            self.assertEqual(chartEntry.isNew, referenceEntry["isNew"])
            self.assertEqual(chartEntry.rank, referenceEntry["rank"])


class TestHistoricalHot100(Base, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = billboard.ChartData("hot-100", date="1979-08-04")
        cls.referenceFile = "1979-08-04-hot-100.json"


class TestHistoricalDigitalAlbums(Base, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = billboard.ChartData("digital-albums", date="2006-08-05")
        cls.referenceFile = "2006-08-05-digital-albums.json"


class TestHistoricalArtist100(Base, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = billboard.ChartData("artist-100", date="2014-08-02")
        cls.referenceFile = "2014-08-02-artist-100.json"
