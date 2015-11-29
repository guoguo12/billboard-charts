#!/usr/bin/env python
import json
import requests
from bs4 import BeautifulSoup

"""billboard.py: Unofficial Python API for accessing ranking charts from Billboard.com."""

__author__ = "Allen Guo"
__license__ = "MIT"
__maintainer__ = "Allen Guo"
__email__ = "guoguo12@gmail.com"


HEADERS = {
    'User-Agent': 'billboard.py (https://github.com/guoguo12/billboard-charts)'}


class ChartEntry:

    def __init__(self, title, artist, peakPos, lastPos, weeks, rank, change):
        self.title = title
        self.artist = artist
        self.peakPos = peakPos
        self.lastPos = lastPos
        self.weeks = weeks
        self.rank = rank
        self.change = change

    def __repr__(self):
        return "'%s' by %s" % (self.title, self.artist)

    def to_JSON(self):
        '''Converts object into JSON; useful for caching'''
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class ChartData:

    def __init__(self, name, date=None, fetch=True, all=False):
        self.name = name
        if date:
            self.date = date
            self.latest = False
        else:
            self.date = None
            self.latest = True
        self.entries = []
        if fetch:
            self.fetchEntries(all=all)

    def __repr__(self):
        if self.latest:
            s = '%s chart (current)' % self.name
        else:
            s = '%s chart from %s' % (self.name, self.date)
        s += '\n' + '-' * len(s)
        for n, entry in enumerate(self.entries):
            s += '\n%s. %s (%s)' % (entry.rank, str(entry), entry.change)
        return s

    def __getitem__(self, key):
        return self.entries[key]

    def __len__(self):
        '''Useful for iterating through shorter/longer charts
        also allows the object to be false if it contains no entries,
        i.e. failed/bad request'''
        return len(self.entries)

    def to_JSON(self):
        '''Converts object and entries into JSON; useful for caching'''
        for entry in self.entries:
            entry = entry.to_JSON()
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def fetchEntries(self, all=False):
        if self.latest:
            url = 'http://www.billboard.com/charts/%s' % (self.name)
        else:
            url = 'http://www.billboard.com/charts/%s/%s' % (
                self.name, self.date)

        html = downloadHTML(url)
        soup = BeautifulSoup(html, 'html.parser')

        for entry_soup in soup.find_all('article', {"class": "chart-row"}):

            # Grab title and artist
            basicInfoSoup = entry_soup.find('div', 'row-title').contents
            title = basicInfoSoup[1].string.strip()

            if (basicInfoSoup[3].find('a')):
                artist = basicInfoSoup[3].a.string.strip()
            else:
                artist = basicInfoSoup[3].string.strip()

            # Grab week data (peak rank, last week's rank, total weeks on
            # chart)
            weekInfoSoup = entry_soup.find('div', 'stats').contents
            peakPos = int(weekInfoSoup[3].find('span', 'value').string.strip())

            lastPos = weekInfoSoup[1].find('span', 'value').string.strip()
            lastPos = 0 if lastPos == '--' else int(lastPos)

            weeks = int(weekInfoSoup[5].find('span', 'value').string.strip())

            # Get current rank
            rank = int(
                entry_soup.find('div', 'row-rank').find('span', 'this-week').string.strip())

            change = lastPos - rank
            if lastPos == 0:
                # New entry
                if weeks > 1:
                    # If entry has been on charts before, it's a re-entry
                    change = "Re-Entry"
                else:
                    change = "New"
            elif change > 0:
                change = "+" + str(change)
            else:
                change = str(change)

            self.entries.append(
                ChartEntry(title, artist, peakPos,
                           lastPos, weeks, rank, change))

        # Hot Shot Debut is the top-ranked new entry, or the first "New" entry
        # we find.
        for entry in self.entries:
            if entry.change == "New":
                entry.change = "Hot Shot Debut"
                break


def downloadHTML(url):
    assert url.startswith('http://')
    req = requests.get(url, headers=HEADERS)
    if req.status_code == 200:
        return req.text
    else:
        return ''
