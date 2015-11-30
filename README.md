billboard.py
============

**billboard.py** is a Python API for accessing ranking charts from Billboard.com.

Installation
------------

To install with pip, run

```
pip install billboard.py
```

You can also clone this repository and run `python setup.py install`.

Quickstart
----------

To download a *Billboard* chart, we use the `ChartData()` constructor.

Let's fetch the current [Hot 100](http://www.billboard.com/charts/hot-100) chart.

```Python
>>> import billboard
>>> chart = billboard.ChartData('hot-100')
```

Now we can look at the chart entries, which are of type `ChartEntry` and have attributes like `artist` and `title`:

```Python
>>> song = chart[0]  # Get no. 1 song on chart
>>> song.title       # Get the title
u'Hello'
>>> song.artist      # Get the artist
u'Adele'
>>> song.weeks       # Get number of weeks on chart
4
```

We can also easily pretty-print the entire chart with:

```Python
print chart
```

which as of 29 November 2015 gives:

```
hot-100 chart (current)
-----------------------
1. 'Hello' by Adele (0)
2. 'Sorry' by Justin Bieber (+1)
3. 'Hotline Bling' by Drake (-1)
4. 'Love Yourself' by Justin Bieber (Hot Shot Debut)
5. 'What Do You Mean?' by Justin Bieber (+1)
6. 'The Hills' by The Weeknd (-2)
7. 'Stitches' by Shawn Mendes (-2)
8. '679' by Fetty Wap Featuring Remy Boyz (-1)
9. 'Wildest Dreams' by Taylor Swift (-1)
10. 'Here' by Alessia Cara (+1)
# ... 90 more lines
```

Full documentation
------------------

### Downloading a chart

Use the `ChartData` constructor to download a chart:

```Python
ChartData(name, date=None, fetch=True, all=False)
```

The arguments are:

* `name` &ndash; The chart name, e.g. `'hot-100'` or `'pop-songs'`. You can browse the Charts section of Billboard.com to find valid chart names; the URL of a chart will look like `http://www.billboard.com/charts/CHART-NAME` ([example](http://www.billboard.com/charts/artist-100)).
* `date` &ndash; The chart date as a string, in YYYY-MM-DD format. If this argument is omitted, the latest chart will be fetched. Again, the best way to find valid dates is by browsing the Billboard website. For the Hot 100 chart, an example of a valid date is `'2015-11-28'`, which gets [this chart](http://www.billboard.com/charts/hot-100/2015-11-28). If this argument is invalid, no exception will be raised; instead, the chart will contain no entries.
* `fetch` &ndash; A boolean indicating whether to fetch the chart data from Billboard.com immediately (at instantiation time). If `False`, the chart data can be populated at a later time using the `fetchEntries()` method.
* `all` &ndash; Deprecated; has no effect.

### Accessing chart entries

If `chart` is a `ChartData` instance, we can ask for its `entries` attribute to get the chart entries (see below) as a list.

For convenience, `chart[x]` is equivalent to `chart.entries[x]`.

### Chart entry attributes

A chart entry (typically a song) is of type `ChartEntry`. A `ChartEntry` instance has the following attributes:

* `title` &ndash; The title of the song.
* `artist` &ndash; The name of the song artist, as formatted on Billboard.com. If there are multiple artists and/or featured artists, they will be included in this string.
* `peakPos` &ndash; The song's peak position on the chart, as an int.
* `lastPos` &ndash; The song's position on the chart last week, as an int. This value is 0 if the song has never been on the chart before.
* `weeks` &ndash; The number of weeks the song has been on the chart. This value is 1 if the song is new on the chart.
* `rank` &ndash; The song's current position on the chart.
* `change` &ndash; A string indicating how the song's position has changed since last week. This may be of the form '+n' or '-n', where 'n' is an integer; this indicates that the song's position has increased or decreased by 'n' points. This string could also be 'New' or 'Re-Entry'; this indicates that the song wasn't on the chart last week because it is either completely new to the chart or re-entering the chart after leaving it for at least a week. Additionally, this string is 'Hot Shot Debut' for the highest-ranked 'New' song.

### More resources

For additional documentation, take a look at the source code for `billboard.py`, or use Python's interactive `help` feature.

If you're stuck or confused: This is a small project, so you can also just email me (Allen). My contact info is on my profile page.

Contributing
------------

Found a bug? Create an issue [here](https://github.com/guoguo12/billboard-charts/issues).

Pull requests are welcome!

### Running tests

Install [tox](https://tox.readthedocs.org/en/latest/) and [nose](https://nose.readthedocs.org/en/latest/).

To run all of the tests, run

```
nosetests
```

Assuming you have both Python 2.7 and 3.4 installed on your machine, you can also run

```
tox
```

to run tests on both versions; see `tox.ini` for configuration details.

Dependencies
------------
* [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/)
* [Requests](http://requests.readthedocs.org/en/latest/) 

License
-------

* This project is licensed under the MIT License.
* The *Billboard* charts are owned by Prometheus Global Media LLC. See Billboard.com's [Terms of Use](http://www.billboard.com/terms-of-use) for more information.
