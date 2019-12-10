import datetime
import unittest
import billboard
from nose.tools import raises


class DateTest(unittest.TestCase):
    def testDateRounding(self):
        """Checks that the Billboard website is rounding dates correctly: it should
        round up to the nearest date on which a chart was published.
        """
        chart = billboard.ChartData("hot-100", date="1000-10-10")
        self.assertEqual(chart.date, "1958-08-04")  # The first Hot 100 chart

        chart = billboard.ChartData("hot-100", date="1996-07-30")
        self.assertEqual(chart.date, "1996-08-03")

    def testPreviousNext(self):
        """Checks that the date, previousDate, and nextDate attributes are parsed
        from the HTML, not computed. Specifically, we shouldn't assume charts are
        always published seven days apart, since (as this example demonstrates)
        this is not true.
        """
        chart = billboard.ChartData("hot-100", date="1962-01-06")
        self.assertEqual(chart.date, "1962-01-06")
        self.assertEqual(chart.previousDate, "1961-12-25")

        chart = billboard.ChartData("hot-100", date="1961-12-25")
        self.assertEqual(chart.date, "1961-12-25")
        self.assertEqual(chart.nextDate, "1962-01-06")

    def testDatetimeDate(self):
        """Checks that ChartData correctly handles datetime objects as the
        date parameter.
        """
        chart = billboard.ChartData("hot-100", datetime.date(2016, 7, 9))
        self.assertEqual(len(chart), 100)
        self.assertEqual(chart.date, "2016-07-09")

    @raises(ValueError)
    def testUnsupportedDateFormat(self):
        """Checks that using an unsupported date format raises an exception."""
        billboard.ChartData("hot-100", date="07-30-1996")

    @raises(ValueError)
    def testEmptyStringDate(self):
        """
        Checks that passing an empty string as the date raises an exception.
        """
        billboard.ChartData("hot-100", date="")

    @raises(ValueError)
    def testInvalidDate(self):
        """Checks that passing a correctly formatted but invalid date raises an exception."""
        billboard.ChartData("hot-100", date="2018-99-99")

    @raises(billboard.BillboardNotFoundException)
    def testFutureDate(self):
        """Checks that passing a date after the date of a chart's last issue raises an exception."""
        billboard.ChartData("hot-100", date="3000-10-10")
