#!/usr/bin/env python

import datetime
import json
import sys

from bs4 import BeautifulSoup
import requests

"""billboard.py: Unofficial Python API for accessing music charts from Billboard.com."""

__author__     = "Allen Guo"
__license__    = "MIT"
__maintainer__ = "Allen Guo"
__email__      = "guoguo12@gmail.com"


HEADERS = {
    'User-Agent': 'billboard.py (https://github.com/guoguo12/billboard-charts)'
}


class BillboardParseException(Exception):
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
    """

    def __init__(self, title, artist, peakPos, lastPos, weeks, rank):
        self.title = title
        self.artist = artist
        self.peakPos = peakPos
        self.lastPos = lastPos
        self.weeks = weeks
        self.rank = rank

    def __repr__(self):
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
        self.previousDate = None
        self.date = date

        self._timeout = timeout

        self.entries = []
        if fetch:
            self.fetchEntries()

    def __repr__(self):
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

    def fetchEntries(self):
        """GETs the corresponding chart data from Billboard.com, then parses
        the data using BeautifulSoup.
        """
        if not self.date:
            # Fetch latest chart
            url = 'http://www.billboard.com/charts/%s' % (self.name)
        else:
            url = 'http://www.billboard.com/charts/%s/%s' % (
                self.name, self.date)

        html = downloadHTML(url, self._timeout)
        soup = BeautifulSoup(html, 'html.parser')

        prevLink = soup.find('a', {'title': 'Previous Week'})
        if prevLink:
            self.previousDate = prevLink.get('href').split('/')[-1]

        currentTime = soup.find('time')
        if currentTime:
            self.date = currentTime.get('datetime')

        for entrySoup in soup.find_all('article', {'class': 'chart-row'}):
            basicInfoSoup = entrySoup.find('div', 'chart-row__title').contents

            try:
                title = basicInfoSoup[1].string or ''
                title = title.strip()
            except:
                message = "Failed to parse title"
                raise BillboardParseException(message)

            try:
                if (basicInfoSoup[3].find('a')):
                    artist = basicInfoSoup[3].a.string.strip()
                else:
                    artist = basicInfoSoup[3].string.strip()
            except:
                message = "Failed to parse artist"
                raise BillboardParseException(message)

            def getRowValue(rowName):
                try:
                    selector = 'div.chart-row__%s .chart-row__value' % rowName
                    return entrySoup.select_one(selector).string.strip()
                except:
                    message = "Failed to parse row value: %s" % rowName
                    raise BillboardParseException(message)

            try:
                peakPos = int(getRowValue('top-spot'))

                lastPos = getRowValue('last-week')
                lastPos = 0 if lastPos == '--' else int(lastPos)

                weeks = int(getRowValue('weeks-on-chart'))
            except BillboardParseException:
                # Assume not available for this chart
                peakPos = lastPos = weeks = None

            try:
                rank = int(
                    entrySoup.select_one('.chart-row__current-week')
                             .string
                             .strip())
            except:
                message = "Failed to parse rank"
                raise BillboardParseException(message)

            entry = ChartEntry(title, artist, peakPos, lastPos, weeks, rank)
            self.entries.append(entry)


def downloadHTML(url, timeout):
    """Downloads and returns the webpage with the given URL.
    Returns an empty string on failure.
    """
    assert url.startswith('http://')
    req = requests.get(url, headers=HEADERS, timeout=timeout)
    if req.status_code == 200:
        return req.text
    else:
        return ''
