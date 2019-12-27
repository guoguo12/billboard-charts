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


# css selector constants
_CHART_NAME_SELECTOR = 'meta[name="twitter:title"]'
_DATE_ELEMENT_SELECTOR = "button.chart-detail-header__date-selector-button"
_PREVIOUS_DATE_SELECTOR = "span.fa-chevron-left"
_NEXT_DATE_SELECTOR = "span.fa-chevron-right"
_ENTRY_LIST_SELECTOR = "div.chart-list-item"
_ENTRY_TITLE_ATTR = "data-title"
_ENTRY_ARTIST_ATTR = "data-artist"
_ENTRY_IMAGE_SELECTOR = "img.chart-list-item__image"
_ENTRY_RANK_ATTR = "data-rank"


# constants for the getPositionRowValue helper function
_ROW_SELECTOR_FORMAT = "div.chart-list-item__%s"
_PEAK_POS_FORMAT = "weeks-at-one"
_LAST_POS_FORMAT = "last-week"
_WEEKS_ON_CHART_FORMAT = "weeks-on-chart"


class BillboardNotFoundException(Exception):
    pass


class BillboardParseException(Exception):
    pass


class ChartEntry:
    """Represents an entry (typically a single track) on a chart.

    Attributes:
        title: The title of the track.
        artist: The name of the track artist, as formatted on Billboard.com.
            If there are multiple artists and/or featured artists, they will
            be included in this string.
        image: The URL of the image for the track.
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

    def __init__(self, title, artist, image, peakPos, lastPos, weeks, rank, isNew):
        self.title = title
        self.artist = artist
        self.image = image
        self.peakPos = peakPos
        self.lastPos = lastPos
        self.weeks = weeks
        self.rank = rank
        self.isNew = isNew

    def __repr__(self):
        return "{}.{}(title={!r}, artist={!r})".format(
            self.__class__.__module__, self.__class__.__name__, self.title, self.artist
        )

    def __str__(self):
        """Returns a string of the form 'TITLE by ARTIST'.
        """
        if self.title:
            s = u"'%s' by %s" % (self.title, self.artist)
        else:
            s = u"%s" % self.artist

        if sys.version_info.major < 3:
            return s.encode(getattr(sys.stdout, "encoding", "") or "utf8")
        else:
            return s

    def json(self):
        """Returns the entry as a JSON string.
        This is useful for caching.
        """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class ChartData:
    """Represents a particular Billboard chart for a particular date.

    Attributes:
        name: The chart name, as a string.
        title: The human-readable chart name, as a string.
        date: The date of the chart.
        previousDate: The date of the previous chart, as a string in YYYY-MM-DD
            format, or None if this information was not available.
        entries: A list of ChartEntry objects, ordered by position on the chart
            (highest first).
    """

    def __init__(self, name, date=None, fetch=True, max_retries=3, timeout=25):
        """Constructs a new ChartData instance.

        Args:
            name: The chart name, e.g. 'hot-100' or 'pop-songs'.
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
            max_retries: The max number of times to retry when requesting data
                (default: 3).
            timeout: The number of seconds to wait for a server response.
                If None, no timeout is applied.
        """
        self.name = name

        if date is not None:
            if not re.match("\d{4}-\d{2}-\d{2}", str(date)):
                raise ValueError("Date argument is not in YYYY-MM-DD format")
            try:
                datetime.datetime(*(int(x) for x in str(date).split("-")))
            except:
                raise ValueError("Date argument is invalid")

        self.date = date
        self.title = ""
        self.previousDate = None

        self._max_retries = max_retries
        self._timeout = timeout

        self.entries = []
        if fetch:
            self.fetchEntries()

    def __repr__(self):
        return "{}.{}({!r}, date={!r})".format(
            self.__class__.__module__, self.__class__.__name__, self.name, self.date
        )

    def __str__(self):
        """Returns the chart as a human-readable string (typically multi-line).
        """
        if not self.date:
            s = "%s chart (current)" % self.name
        else:
            s = "%s chart from %s" % (self.name, self.date)
        s += "\n" + "-" * len(s)
        for n, entry in enumerate(self.entries):
            s += "\n%s. %s" % (entry.rank, str(entry))
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
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def _parseOldStylePage(self, soup):
        dateElement = soup.select_one(_DATE_ELEMENT_SELECTOR)
        if dateElement:
            dateText = dateElement.text.strip()
            curDate = datetime.datetime.strptime(dateText, "%B %d, %Y")
            self.date = curDate.strftime("%Y-%m-%d")

        prevWeek = soup.select_one(_PREVIOUS_DATE_SELECTOR)
        nextWeek = soup.select_one(_NEXT_DATE_SELECTOR)
        if prevWeek and prevWeek.parent.get("href"):
            self.previousDate = prevWeek.parent.get("href").split("/")[-1]
        if nextWeek and nextWeek.parent.get("href"):
            self.nextDate = nextWeek.parent.get("href").split("/")[-1]

        for entrySoup in soup.select(_ENTRY_LIST_SELECTOR):
            try:
                title = entrySoup[_ENTRY_TITLE_ATTR].strip()
            except:
                message = "Failed to parse title"
                raise BillboardParseException(message)

            try:
                artist = entrySoup[_ENTRY_ARTIST_ATTR].strip() or ""
            except:
                message = "Failed to parse artist"
                raise BillboardParseException(message)

            if artist == "":
                title, artist = artist, title

            try:
                imageSoup = entrySoup.select_one(_ENTRY_IMAGE_SELECTOR)
                if imageSoup.has_attr("data-src"):
                    image = imageSoup["data-src"]
                else:
                    image = imageSoup["src"]
            except:
                message = "Failed to parse image"
                raise BillboardParseException(message)

            try:
                rank = int(entrySoup[_ENTRY_RANK_ATTR].strip())
            except:
                message = "Failed to parse rank"
                raise BillboardParseException(message)

            def getPositionRowValue(rowName, ifNoValue=None):
                try:
                    selector = _ROW_SELECTOR_FORMAT % rowName
                    selected = entrySoup.select(selector)
                    # We get the first element of selected because there are two
                    # elements matching _LAST_POS_FORMAT and we want the first
                    # one (the second is the position two weeks previous)
                    if (
                        not selected
                        or selected[0].string is None
                        or selected[0].string == "-"
                    ):
                        return ifNoValue
                    else:
                        return int(selected[0].string.strip())
                except:
                    message = "Failed to parse row value: %s" % rowName
                    raise BillboardParseException(message)

            if self.date:
                peakPos = getPositionRowValue(_PEAK_POS_FORMAT)
                lastPos = getPositionRowValue(_LAST_POS_FORMAT, ifNoValue=0)
                weeks = getPositionRowValue(_WEEKS_ON_CHART_FORMAT, ifNoValue=1)
                isNew = True if weeks == 1 else False
            else:
                peakPos = lastPos = weeks = None
                isNew = False

            entry = ChartEntry(
                title, artist, image, peakPos, lastPos, weeks, rank, isNew
            )
            self.entries.append(entry)

    def _parseNewStylePage(self, soup):
        dateElement = soup.select_one("button.date-selector__button.button--link")
        if dateElement:
            dateText = dateElement.text.strip()
            curDate = datetime.datetime.strptime(dateText, "%B %d, %Y")
            self.date = curDate.strftime("%Y-%m-%d")

        self.previousDate = soup.select_one("#charts")["data-previous-chart-date"]
        self.nextDate = soup.select_one("#charts")["data-chart-next-date"]

        for entrySoup in soup.select("li.chart-list__element"):

            def getEntryAttr(selector):
                return entrySoup.select_one(selector).text.strip()

            try:
                title = getEntryAttr("span.chart-element__information__song")
            except:
                message = "Failed to parse title"
                raise BillboardParseException(message)

            try:
                artist = getEntryAttr("span.chart-element__information__artist") or ""
            except:
                message = "Failed to parse artist"
                raise BillboardParseException(message)

            if artist == "":
                title, artist = artist, title

            # TODO: Parse the image
            image = None

            try:
                rank = int(getEntryAttr("span.chart-element__rank__number"))
            except:
                message = "Failed to parse rank"
                raise BillboardParseException(message)

            def getMeta(attribute, ifNoValue=None):
                try:
                    selected = entrySoup.select_one(
                        "span.chart-element__meta.text--%s" % attribute
                    )
                    if (
                        not selected
                        or selected.string is None
                        or selected.string == "-"
                    ):
                        return ifNoValue
                    else:
                        return int(selected.string.strip())
                except:
                    message = "Failed to parse metadata value: %s" % attribute
                    raise BillboardParseException(message)

            if self.date:
                peakPos = getMeta("peak")
                lastPos = getMeta("last", ifNoValue=0)
                weeks = getMeta("week", ifNoValue=1)
                isNew = True if weeks == 1 else False
            else:
                peakPos = lastPos = weeks = None
                isNew = False

            entry = ChartEntry(
                title, artist, image, peakPos, lastPos, weeks, rank, isNew
            )
            self.entries.append(entry)

    def _parsePage(self, soup):
        chartTitleElement = soup.select_one(_CHART_NAME_SELECTOR)
        if chartTitleElement:
            self.title = chartTitleElement.get("content", "").split("|")[0].strip()

        if soup.select("table"):
            self._parseOldStylePage(soup)
        else:
            self._parseNewStylePage(soup)

    def fetchEntries(self):
        """GETs the corresponding chart data from Billboard.com, then parses
        the data using BeautifulSoup.
        """
        if not self.date:
            # Fetch latest chart
            url = "http://www.billboard.com/charts/%s" % (self.name)
        else:
            url = "http://www.billboard.com/charts/%s/%s" % (self.name, self.date)

        session = _get_session_with_retries(max_retries=self._max_retries)
        req = session.get(url, timeout=self._timeout)
        if req.status_code == 404:
            message = "Chart not found (perhaps the name is misspelled?)"
            raise BillboardNotFoundException(message)
        req.raise_for_status()

        soup = BeautifulSoup(req.text, "html.parser")
        self._parsePage(soup)


def charts():
    """Gets a list of all Billboard charts from Billboard.com.
    """
    session = _get_session_with_retries(max_retries=3)
    req = session.get("https://www.billboard.com/charts", timeout=25)
    req.raise_for_status()
    soup = BeautifulSoup(req.text, "html.parser")
    return [
        link["href"].split("/")[-1]
        for link in soup.findAll("a", {"class": "chart-panel__link"})
    ]


def _get_session_with_retries(max_retries):
    session = requests.Session()
    session.mount("", requests.adapters.HTTPAdapter(max_retries=max_retries))
    return session
