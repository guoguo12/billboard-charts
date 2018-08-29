#!/usr/bin/env python

import datetime
import json
import re
import sys

from bs4 import BeautifulSoup
import requests

"""billboard.py: Unofficial Python API for accessing music charts from Billboard.com."""

__author__ = "Allen Guo"
__license__ = "MIT"
__maintainer__ = "Allen Guo"
__email__ = "guoguo12@gmail.com"


HEADERS = {
    'User-Agent': 'billboard.py (https://github.com/guoguo12/billboard-charts)'
}

_SESSION = requests.session()

# css selector constants
_DATE_ELEMENT_SELECTOR = 'button.chart-detail-header__date-selector-button'
_PREVIOUS_DATE_SELECTOR = 'span.fa-chevron-left'
_NEXT_DATE_SELECTOR = 'span.fa-chevron-right'
_TOP_TITLE_SELECTOR = 'div.chart-number-one__title'
_TOP_ARTIST_SELECTOR = 'div.chart-number-one__artist'
_TOP_LAST_POS_SELECTOR = 'div.chart-number-one__last-week'
_TOP_WEEKS_SELECTOR = 'div.chart-number-one__weeks-on-chart'
_ENTRY_LIST_SELECTOR = 'div.chart-list-item'
_ENTRY_TITLE_ATTR = 'data-title'
_ENTRY_ARTIST_ATTR = 'data-artist'
_ENTRY_RANK_ATTR = 'data-rank'

# constants for the getPositionRowValue helper function
_ROW_SELECTOR_FORMAT = 'div.chart-list-item__%s'
_PEAK_POS_FORMAT = 'weeks-at-one'
_LAST_POS_FORMAT = 'last-week'
_WEEKS_ON_CHART_FORMAT = 'weeks-on-chart'


class BillboardException(Exception):
    pass


class BillboardParseException(BillboardException):
    pass


class BillboardContentException(BillboardException):
    pass


class BillboardEmptyResponseException(BillboardContentException):
    pass


class BillboardNotFoundException(BillboardContentException):
    pass


class ChartEntry:
    """Represents an entry (typically a single track) on a chart.

    Attributes:
        title: The title of the track.
        artist: The name of the track artist, as formatted on Billboard.com.
            If there are multiple artists and/or featured artists, they will
            be included in this string.
        peakPos: The track's peak position on the chart at any point in time,
            including future dates, as an int (or None if the chart does not
            include this information).
        lastPos: The track's position on the previous week's chart, as an int
            (or None if the chart does not include this information).
            This value is 0 if the track was not on the previous week's chart.
        weeks: The number of weeks the track has been or was on the chart,
            including future dates (up until the present time).
        rank: The track's position on the chart, as an int.
        isNew: Whether the track is new to the chart, as a boolean.
    """

    def __init__(self, title, artist, peakPos, lastPos, weeks, rank, isNew):
        self.title = title
        self.artist = artist
        self.peakPos = peakPos
        self.lastPos = lastPos
        self.weeks = weeks
        self.rank = rank
        self.isNew = isNew

    def __repr__(self):
        return '{}.{}(title={!r}, artist={!r})'.format(self.__class__.__module__,
                                                       self.__class__.__name__,
                                                       self.title,
                                                       self.artist)

    def __str__(self):
        """Returns a string of the form 'TITLE by ARTIST'.
        """
        if self.title:
            s = u"'%s' by %s" % (self.title, self.artist)
        else:
            s = u"%s" % self.artist

        if sys.version_info.major < 3:
            return s.encode(getattr(sys.stdout, 'encoding', '') or 'utf8')
        else:
            return s

    def json(self):
        """Returns the entry as a JSON string.
        This is useful for caching.
        """
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class ChartData:
    """Represents a particular Billboard chart for a particular date.

    Attributes:
        name: The chart name, as a string.
        date: The date of the chart.
        previousDate: The date of the previous chart, as a string in YYYY-MM-DD
            format, or None if this information was not available.
        entries: A list of ChartEntry objects, ordered by position on the chart
            (highest first).
    """

    def __init__(self, name, date=None, fetch=True, timeout=25):
        """Constructs a new ChartData instance.

        Args:
            name: The chart name, e.g. 'hot-100' or 'pop-songs'.
                You can browse the Charts section of Billboard.com to find
                valid chart names; the URL of a chart will look like
                "http://www.billboard.com/charts/CHART-NAME".
            date: The chart date, as a string in YYYY-MM-DD format.
                By default, the latest chart is fetched.
                If the argument is not a date on which a chart was published,
                Billboard automatically rounds dates up to the nearest date on
                which a chart was published.
                If this argument is invalid, no exception will be raised;
                instead, the chart will contain no entries.
            fetch: A boolean indicating whether to fetch the chart data from
                Billboard.com immediately (at instantiation time).
                If False, the chart data can be populated at a later time
                using the fetchEntries() method.
            timeout: The number of seconds to wait for a server response.
                If None, no timeout is applied.
        """
        self.name = name

        if date is not None:
            try:
                datetime.datetime(*(int(x) for x in str(date).split('-')))
            except ValueError as e:
                raise ValueError('Date argument is invalid. ' + str(e))

        self.date = date
        self.previousDate = None

        self._timeout = timeout

        self.entries = []
        if fetch:
            self.fetchEntries()

    def __repr__(self):
        return '{}.{}({!r}, date={!r})'.format(self.__class__.__module__,
                                               self.__class__.__name__,
                                               self.name, self.date)

    def __str__(self):
        """Returns the chart as a human-readable string (typically multi-line).
        """
        if not self.date:
            s = '%s chart (current)' % self.name
        else:
            s = '%s chart from %s' % (self.name, self.date)
        s += '\n' + '-' * len(s)
        for n, entry in enumerate(self.entries):
            s += '\n%s. %s' % (entry.rank, str(entry))
        return s

    def __getitem__(self, key):
        """Returns the (key + 1)-th chart entry; i.e., chart[0] refers to the
        top entry on the chart.
        """
        return self.entries[key]

    def __len__(self):
        """Returns the number of entries in the chart.
        A length of zero may indicated a failed/bad request.
        """
        return len(self.entries)

    def json(self):
        """Returns the entry as a JSON string.
        This is useful for caching.
        """
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def _fetchSoup(self):
        """GETs the corresponding chart from Billboard.com and returns it
        as a BeautifulSoup object.
        """
        if not self.date:
            # Fetch latest chart
            url = 'https://www.billboard.com/charts/%s' % (self.name)
        else:
            url = 'https://www.billboard.com/charts/%s/%s' % (
                self.name, self.date)

        resp = _SESSION.get(url, headers=HEADERS, timeout=self._timeout)
        if resp.status_code == 404:
            message = "Chart not found (perhaps the name is misspelled?)"
            raise BillboardNotFoundException(message)
        resp.raise_for_status()

        return BeautifulSoup(resp.text, 'html.parser')

    def _parseTopEntry(self, soup):
        '''Parse and return a ChartEntry object for the #1 entry on the chart'''
        try:
            topTitle = soup.select_one(_TOP_TITLE_SELECTOR).string.strip()
        except AttributeError:
            message = "Failed to parse top track title"
            raise BillboardParseException(message)

        try:
            topArtistElement = soup.select_one(_TOP_ARTIST_SELECTOR) or ''
            if topArtistElement == '':
                topTitle, topArtist = '', topTitle
            elif topArtistElement.a is None:
                topArtist = topArtistElement.getText().strip()
            else:
                topArtist = topArtistElement.a.getText().strip()
        except:
            message = "Failed to parse top track artist"
            raise BillboardParseException(message)

        if self.date:
            topPeakPos = 1
            try:
                topLastPos = int(soup.select_one(
                    _TOP_LAST_POS_SELECTOR).string.strip())
            except (AttributeError, ValueError):
                # if there is no div with class div.chart-number-one__last-week, that means it was the top song the prior week
                topLastPos = 1

            topWeeksElement = soup.select_one(_TOP_WEEKS_SELECTOR)
            topWeeks = int(topWeeksElement.string.strip()
                           ) if topWeeksElement is not None else 0
            topIsNew = True if topWeeks == 0 else False
        else:
            topPeakPos = topLastPos = topWeeks = None
            topIsNew = False

        return ChartEntry(topTitle, topArtist, topPeakPos,
                          topLastPos, topWeeks, 1, topIsNew)

    def getPositionRowValue(self, entrySoup, rowName):
        '''Get the value of a particular position metric: last position,
        peak position, number of weeks, etc. Raises BillBoardParseException'''
        try:
            selector = _ROW_SELECTOR_FORMAT % rowName
            selected = entrySoup.select_one(selector)
            if selected is None or selected.string == '-':
                return 0
            else:
                return int(selected.string.strip())
        except AttributeError:
            message = "Failed to parse row value: %s" % rowName
            raise BillboardParseException(message)

    def _parseEntryAttr(self, entrySoup, attr):
        '''Get a specific attribute from an entrySoup and raise a specific
        BillboardParseException if the soup does not have that attribute'''
        try:
            return entrySoup[attr].strip()
        except:
            message = "Failed to parse " + attr
            raise BillboardParseException(message)

    def _parseEntry(self, entrySoup):
        '''Parse a ChartEntry from a single entry soup'''
        def entryAttr(attr): return self._parseEntryAttr(entrySoup, attr)
        title = entryAttr(_ENTRY_TITLE_ATTR)
        artist = entryAttr(_ENTRY_ARTIST_ATTR)
        rank = int(entryAttr(_ENTRY_RANK_ATTR))

        if not artist:
            title, artist = artist, title

        if self.date:
            peakPos = self.getPositionRowValue(entrySoup, _PEAK_POS_FORMAT)
            lastPos = self.getPositionRowValue(entrySoup, _LAST_POS_FORMAT)
            weeks = self.getPositionRowValue(entrySoup, _WEEKS_ON_CHART_FORMAT)
            peakPos = rank if peakPos == 0 else peakPos
            isNew = True if weeks == 0 else False
        else:
            peakPos = lastPos = weeks = None
            isNew = False

        return ChartEntry(title, artist, peakPos,
                          lastPos, weeks, rank, isNew)

    def _setDates(self, soup):
        '''Set this ChartData's date properties given a chart's soup'''
        dateElement = soup.select_one(_DATE_ELEMENT_SELECTOR)
        if dateElement:
            dateText = dateElement.text.strip()
            curDate = datetime.datetime.strptime(dateText, '%B %d, %Y')
            self.date = curDate.strftime('%Y-%m-%d')
        prevWeek = soup.select_one(_PREVIOUS_DATE_SELECTOR)
        nextWeek = soup.select_one(_NEXT_DATE_SELECTOR)
        if prevWeek and prevWeek.parent.get('href'):
            self.previousDate = prevWeek.parent.get('href').split('/')[-1]
        if nextWeek and nextWeek.parent.get('href'):
            self.nextDate = nextWeek.parent.get('href').split('/')[-1]

    def fetchEntries(self):
        '''GETs the corresponding chart data from Billboard.com, then parses
        the data using BeautifulSoup.
        '''
        soup = self._fetchSoup()
        self._setDates(soup)
        entries = soup.select(_ENTRY_LIST_SELECTOR)

        if not entries:
            message = "Billboard returned a blank page. (Has this chart been released yet?)"
            raise BillboardEmptyResponseException(message)

        topEntry = self._parseTopEntry(soup)
        self.entries = [topEntry] + \
            [self._parseEntry(entry) for entry in entries]


def charts():
    '''Returns a list of charts available from billboard.com'''
    resp = _SESSION.get('https://www.billboard.com/charts',
                        headers=HEADERS, timeout=25)
    if not resp.ok:
        resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    return [c['href'].split('/')[-1] for c in soup.select('a.chart-panel__link')]
