#!/usr/bin/env python

"""billboard.py: Unofficial Python API for accessing ranking charts from Billboard.com."""

__author__     = "Allen Guo"
__license__    = "MIT"
__maintainer__ = "Allen Guo"
__email__      = "guoguo12@gmail.com"

import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'billboard.py (https://github.com/guoguo12/billboard-charts)'}


class ChartEntry:

    def __init__(self, title, artist, album, peakPos, lastPos, weeks, rank, change):
        self.title = title
        self.artist = artist
        self.album = album
        self.peakPos = peakPos
        self.lastPos = lastPos
        self.weeks = weeks
        self.rank = rank
        self.change = change

    def __repr__(self):
        if self.album:
            return "'%s' by %s from '%s'" % (self.title, self.artist, self.album)
        else:
            return "'%s' by %s" % (self.title, self.artist)


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

    def fetchEntries(self, all=False):
        if self.latest:
            pages = 10 if all else 1
            url = 'http://www.billboard.com/charts/%s' % (self.name)
        else:
            pages = 1  # Only first page is available for old charts
            url = 'http://www.billboard.com/charts/%s/%s' % (self.date, self.name)
        for page in xrange(0, pages):
            params = {'page': str(page)}
            html = downloadHTML(url, params=params)
            soup = BeautifulSoup(html)
            for entry_soup in soup.find_all('article', 'song_review'):
                title = entry_soup.header.h1.string.strip()
                chartInfoSoup = entry_soup.header.find('p', 'chart_info')
                if len(chartInfoSoup.contents) >= 4:
                    # Chart info includes both artist and album info
                    artist = chartInfoSoup.contents[1].string
                    if chartInfoSoup.contents[3].string:
                        album = chartInfoSoup.contents[3].string.strip()
                       	# Index where album info is stored might be off by one depending on client/IP.
                    elif chartInfoSoup.contents[4].string:
                        album = chartInfoSoup.contents[4].string.strip()
                    else:
                        album = None
                else:
                    album = None  # Chart info includes only artist info
                    if chartInfoSoup.find('a'):
                        # Artist name is linked
                        artist = chartInfoSoup.find('a').string.strip()
                    else:
                        # Artist name is not linked
                        artist = chartInfoSoup.contents[0].string.strip()
                pos_soups = entry_soup.header.ul.find_all('li')
                peakPos = int(pos_soups[0].contents[2].strip())
                lastPosStr = pos_soups[1].contents[2].encode('ascii', 'ignore').strip()
                if lastPosStr:
                    # Last position exists
                    lastPos = int(lastPosStr)
                else:
                    # No last position
                    lastPos = 0
                weeks = int(pos_soups[2].contents[2].strip())
                rank = entry_soup.header.find('span', 'chart_position').string.strip()
                change = lastPos - int(rank)
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
                self.entries.append(ChartEntry(title, artist, album, peakPos, lastPos, weeks, rank, change))
        # Hot Shot Debut is the top-ranked new entry, or the first "New" entry we find.
        for entry in self.entries:
			if entry.change == "New":
				entry.change = "Hot Shot Debut"
				break


def downloadHTML(url, params):
    assert url.startswith('http://')
    req = requests.get(url, params=params, headers=HEADERS)
    if req.status_code == 200:
        return req.text
    else:
        return ''
