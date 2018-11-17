import datetime
import unittest
import billboard
from nose.tools import raises


class DateTest(unittest.TestCase):
    def test_date_rounding(self):
        """Checks that the we are rounding dates correctly: it should
        round up to the nearest date on which a chart was published.
        """
        chart = billboard.YearEnd('hot-100-songs', date='1000')
        self.assertEqual(chart.date, '2006')  # The first year end hot 100 songs chart

        chart = billboard.YearEnd('hot-100-songs', date='2006')
        self.assertEqual(chart.date, '2006')

    def test_previous_next(self):
        """Checks that the date, previousDate, and nextDate attributes are parsed
        from the HTML, not computed. Specifically, we shouldn't assume charts are
        always published seven days apart, since (as this example demonstrates)
        this is not true.
        """
        chart = billboard.YearEnd('hot-100-songs', date='2007')
        self.assertEqual(chart.date, '2007')
        self.assertEqual(chart.previousDate, '2006')

        chart = billboard.YearEnd('hot-100-songs', date='2007')
        self.assertEqual(chart.date, '2007')
        self.assertEqual(chart.nextDate, '2008')

    @raises(AttributeError)
    def test_uhhh(self):
        """Checks that nextDate raises an AttributeError when there are no more
        charts. For example, if 2017 is the last chart then it should raise an
        AttributeError since there is not an 2018 chart yet.
        """
        chart = billboard.YearEnd('hot-100-songs')
        chart = billboard.YearEnd('hot-100-songs', chart.nextDate)

    def test_datetime_date(self):
        """Checks that YearEnd correctly handles datetime objects as the
        date parameter.
        """
        chart = billboard.YearEnd('hot-100-songs', datetime.date(2015, 7, 9))
        self.assertEqual(len(chart), 100)
        self.assertEqual(chart.date, '2015')

    @raises(ValueError)
    def test_unsupported_date_format(self):
        """Checks that using an unsupported date format raises an exception."""
        billboard.YearEnd('hot-100-songs', date='07-30-1996')

    @raises(ValueError)
    def test_empty_string_date(self):
        """
        Checks that passing an empty string as the date raises an exception.
        """
        billboard.YearEnd('hot-100-songs', date='')
