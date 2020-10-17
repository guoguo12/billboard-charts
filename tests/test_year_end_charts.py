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

    def testYear(self):
        self.assertIsNotNone(self.chart.year)

    def testTitle(self):
        self.assertEqual(self.chart.title, self.expectedTitle)

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
