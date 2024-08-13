#!/usr/bin/env python

import datetime
import json
import re
import sys
import warnings

from bs4 import BeautifulSoup
import requests

"""billboard.py: Unofficial Python API for accessing music charts from Billboard.com."""

__author__ = "Allen Guo"
__license__ = "MIT"
__maintainer__ = "Allen Guo"
__email__ = "guoguo12@gmail.com"


# css selector constants
_CHART_NAME_SELECTOR = 'meta[property="og:title"]'
_DATE_ELEMENT_SELECTOR = "button.chart-detail-header__date-selector-button"
_PREVIOUS_DATE_SELECTOR = "span.fa-chevron-left"
_NEXT_DATE_SELECTOR = "span.fa-chevron-right"
_ENTRY_LIST_SELECTOR = "div.chart-list-item"
_ENTRY_TITLE_ATTR = "data-title"
_ENTRY_ARTIST_ATTR = "data-artist"
_ENTRY_IMAGE_SELECTOR = "img.chart-list-item__image"
_ENTRY_RANK_ATTR = "data-rank"
# On new style pages, the column headings of chart data
# Used to determine if the "Award" column is present in the chart.
_CHART_HEADER_CELLS = "div.o-chart-results-list-header__item span"

# constants for the getMinistatsCellValue helper function
_MINISTATS_CELL = "div.chart-list-item__ministats-cell"
_MINISTATS_CELL_HEADING = "span.chart-list-item__ministats-cell-heading"


class BillboardNotFoundException(Exception):
    pass


class BillboardParseException(Exception):
    pass


class UnsupportedYearWarning(UserWarning):
    pass


class ChartEntry:
    """Represents an entry (typically a single track) on a chart.

    Attributes:
        title: The title of the track.
        artist: The name of the track artist, as formatted on Billboard.com.
            If there are multiple artists and/or featured artists, they will
            be included in this string.
        image: The URL of the image for the track.
        peakPos: The track's peak position on the chart as of the chart date,
            as an int (or None if the chart does not include this information).
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
        """Returns a string of the form 'TITLE by ARTIST'."""
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


class YearEndChartEntry(ChartEntry):
    """Represents an entry (typically a single track) on a year-end chart.

    Attributes:
        title: The title of the track.
        artist: The name of the track artist, as formatted on Billboard.com.
            If there are multiple artists and/or featured artists, they will
            be included in this string.
        image: The URL of the image for the track.
        rank: The track's position on the chart, as an int.
        year: The chart's year, as an int.
    """

    def __init__(self, title, artist, image, rank):
        self.title = title
        self.artist = artist
        self.image = image
        self.rank = rank


class ChartData:
    """Represents a particular Billboard chart for a particular date.

    Attributes:
        name: The chart name, as a string.
        title: The human-readable chart name, as a string.
        date: The date of the chart.
        previousDate: Deprecated. Is always None or an empty string.
        nextDate: Deprecated. Is always None or an empty string.
        entries: A list of ChartEntry objects, ordered by position on the chart
            (highest first).
    """

    def __init__(
        self, name, date=None, year=None, fetch=True, max_retries=5, timeout=25
    ):
        """Constructs a new ChartData instance.

        Args:
            name: The chart name, e.g. 'hot-100' or 'pop-songs'.
            date: The chart date, as a string in YYYY-MM-DD format.
                By default, the latest chart is fetched.
                If the argument is not a date on which a chart was published,
                Billboard automatically rounds dates up to the nearest date on
                which a chart was published.
                If this argument is invalid, no exception will be raised;
                instead, the chart will contain no entries. Cannot supply
                both `date` and `year`.
            year: The chart year, if requesting a year-end chart. Must
                be a string in YYYY format. Cannot supply both `date`
                and `year`.
            fetch: A boolean indicating whether to fetch the chart data from
                Billboard.com immediately (at instantiation time).
                If False, the chart data can be populated at a later time
                using the fetchEntries() method.
            max_retries: The max number of times to retry when requesting data
                (default: 5).
            timeout: The number of seconds to wait for a server response.
                If None, no timeout is applied.
        """
        self.name = name

        # Check if the user supplied both a date and a year (they can't)
        if sum(map(bool, [date, year])) >= 2:
            raise ValueError("Can't supply both `date` and `year`.")

        if date is not None:
            if not re.match(r"\d{4}-\d{2}-\d{2}", str(date)):
                raise ValueError("Date argument is not in YYYY-MM-DD format")
            try:
                datetime.datetime(*(int(x) for x in str(date).split("-")))
            except:
                raise ValueError("Date argument is invalid")

        if year is not None:
            if not re.match(r"\d{4}", str(year)):
                raise ValueError("Year argument is not in YYYY format")

        self.date = date
        self.year = year
        self.title = ""

        self._max_retries = max_retries
        self._timeout = timeout

        self.entries = []
        if fetch:
            self.fetchEntries()

    def __repr__(self):
        if self.year:
            return "{}.{}({!r}, year={!r})".format(
                self.__class__.__module__, self.__class__.__name__, self.name, self.year
            )
        return "{}.{}({!r}, date={!r})".format(
            self.__class__.__module__, self.__class__.__name__, self.name, self.date
        )

    def __str__(self):
        """Returns the chart as a human-readable string (typically multi-line)."""
        if self.year:
            s = "%s chart (%s)" % (self.name, self.year)
        elif not self.date:
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

    # TODO: As of 2021-11-20, this doesn't seem to be used anymore, since
    # Billboard has made their styling consistent across charts.
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
        else:
            self.previousDate = ""
        if nextWeek and nextWeek.parent.get("href"):
            self.nextDate = nextWeek.parent.get("href").split("/")[-1]
        else:
            self.nextDate = ""

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

            if self.date:

                # "Ministats" is the name in the Billboard.com source code for
                # the stats under each chart entry
                def getMinistatsCellValue(fieldName, ifNoValue=None):
                    try:
                        for ministat in entrySoup.select(_MINISTATS_CELL):
                            heading = ministat.select_one(_MINISTATS_CELL_HEADING)
                            headingText = heading.string.strip().lower()
                            if headingText == fieldName:
                                value = ministat.text.split(u"\xa0")[0].strip()
                                if value is None or value == "-":
                                    return ifNoValue
                                else:
                                    return int(value)
                        return ifNoValue
                    except Exception as e:
                        print(e)
                        message = "Failed to parse ministats cell value: %s" % fieldName
                        raise BillboardParseException(message)

                peakPos = getMinistatsCellValue("peak")
                lastPos = getMinistatsCellValue("last", ifNoValue=0)
                weeks = getMinistatsCellValue("weeks", ifNoValue=1)
                isNew = True if weeks == 1 else False
            else:
                peakPos = lastPos = weeks = None
                isNew = False

            entry = ChartEntry(
                title, artist, image, peakPos, lastPos, weeks, rank, isNew
            )
            self.entries.append(entry)

    def _pageHasAwardColumn(self, soup):
        cols = soup.select(_CHART_HEADER_CELLS)
        for span in cols:
            if "award" in span.string.lower():
                return True
        return False

    def _parseNewStylePage(self, soup):
        dateElement = soup.select_one("#chart-date-picker")
        if dateElement:
            self.date = dateElement["data-date"]

        # TODO: Fix these, if possible. These used to be exposed directly in the
        # HTML. There were tests for these, removed in
        # 4d2f4ad06719341faa0bc2df5568c6354d66fc3c. If this is ever fixed,
        # update the documentation above.
        self.previousDate = None
        self.nextDate = None

        for entrySoup in soup.select("ul.o-chart-results-list-row"):

            def getEntryAttr(which_li, selector):
                element = entrySoup.select("li")[which_li].select_one(selector)
                if element:
                    return element.text.strip()
                return None

            try:
                title = getEntryAttr(3, "#title-of-a-story")
            except:
                message = "Failed to parse title"
                raise BillboardParseException(message)

            try:
                artist = getEntryAttr(3, "#title-of-a-story + span.c-label") or ""
            except:
                message = "Failed to parse artist"
                raise BillboardParseException(message)

            # For artist charts like the Artist 100
            if artist == "":
                title, artist = artist, title

            imageElement = entrySoup.select_one("li:nth-child(2) img")
            if imageElement:
                image = imageElement.get("data-lazy-src", None)
            else:
                image = None

            try:
                rank = int(getEntryAttr(0, "span.c-label"))
            except:
                message = "Failed to parse rank"
                raise BillboardParseException(message)

            def getMeta(attribute, which_li, ifNoValue=None):
                try:
                    selected = entrySoup.select_one("ul").select("li")[which_li]

                    if not selected:
                        return ifNoValue

                    value = selected.text.strip()
                    if value == "-":
                        return ifNoValue
                    else:
                        return int(value)
                except:
                    message = "Failed to parse metadata value: %s" % attribute
                    raise BillboardParseException(message)

            # Some pages do not show an award column in their chart data.
            # If missing, this changes the column number offsets.
            awardColumnOffset = 0 if self._pageHasAwardColumn(soup) else -1
            if self.date:
                peakPos = getMeta("peak", 4 + awardColumnOffset)
                lastPos = getMeta("last", 3 + awardColumnOffset, ifNoValue=0)
                weeks = getMeta("week", 5 + awardColumnOffset, ifNoValue=1)
                isNew = True if weeks == 1 else False
            else:
                peakPos = lastPos = weeks = None
                isNew = False

            entry = ChartEntry(
                title, artist, image, peakPos, lastPos, weeks, rank, isNew
            )
            self.entries.append(entry)

    def _parseYearEndPage(self, soup):
        # This is for consistency with Billboard.com's former title style
        self.title += " - Year-End"

        # Determine the next and previous year-end chart
        years = [
            int(li.text.strip()) for li in soup.select("div.a-chart-o-nav-left ul li")
        ]
        current_year = int(self.year)
        min_year, max_year = min(years), max(years)
        if current_year in years:
            self.previousYear = (
                str(current_year - 1) if current_year > min_year else None
            )
            self.nextYear = str(current_year + 1) if current_year < max_year else None
        else:
            # Warn the user about having requested an unsupported year.
            msg = """
            %s is not a supported year-end chart from Billboard.
            Results may be incomplete, inconsistent, or missing entirely.
            The min and max supported years for the '%s' chart are %d and %d, respectively.
            """ % (
                current_year,
                self.name,
                min_year,
                max_year,
            )
            warnings.warn(UnsupportedYearWarning(msg))

            # Assign  next and previous years (can be non-null if outside by 1)
            if current_year in [min_year - 1, max_year + 1]:
                self.nextYear = min_year if current_year < min_year else None
                self.previousYear = max_year if current_year > max_year else None
            else:
                self.previousYear = self.nextYear = None

        # TODO: This is all copied from `_parseNewStylePage` above, but with
        # worse error-handling. They should be merged.
        for entrySoup in soup.select("ul.o-chart-results-list-row"):

            def getEntryAttr(which_li, selector):
                element = entrySoup.select("li")[which_li].select_one(selector)
                if element:
                    return element.text.strip()
                return None

            title = getEntryAttr(3, "#title-of-a-story")
            artist = getEntryAttr(3, "#title-of-a-story + span.c-label") or ""
            if artist == "":
                title, artist = artist, title
            image = None
            rank = int(getEntryAttr(0, "span.c-label"))

            entry = YearEndChartEntry(title, artist, image, rank)
            self.entries.append(entry)

    def _parsePage(self, soup):
        chartTitleElement = soup.select_one(_CHART_NAME_SELECTOR)
        if chartTitleElement:
            self.title = re.sub(
                " Chart$",
                "",
                chartTitleElement.get("content", "").split("|")[0].strip(),
            )

        if self.year:
            self._parseYearEndPage(soup)
        elif soup.select("table"):
            self._parseOldStylePage(soup)
        else:
            self._parseNewStylePage(soup)

    def fetchEntries(self):
        """GETs the corresponding chart data from Billboard.com, then parses
        the data using BeautifulSoup.
        """
        if not self.date:
            if not self.year:
                # Fetch latest chart
                url = "https://www.billboard.com/charts/%s" % (self.name)
            else:
                url = "https://www.billboard.com/charts/year-end/%s/%s" % (
                    self.year,
                    self.name,
                )
        else:
            url = "https://www.billboard.com/charts/%s/%s" % (self.name, self.date)

        session = _get_session_with_retries(max_retries=self._max_retries)
        req = session.get(url, timeout=self._timeout)
        if req.status_code == 404:
            message = "Chart not found (perhaps the name is misspelled?)"
            raise BillboardNotFoundException(message)
        req.raise_for_status()

        soup = BeautifulSoup(req.text, "html.parser")
        self._parsePage(soup)


def _get_session_with_retries(max_retries):
    session = requests.Session()
    session.mount(
        "https://www.billboard.com",
        requests.adapters.HTTPAdapter(max_retries=max_retries),
    )
    return session
