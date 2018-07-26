billboard.py
============

[![Build Status](https://travis-ci.org/guoguo12/billboard-charts.svg)](https://travis-ci.org/guoguo12/billboard-charts)

**billboard.py** is a Python API for accessing music charts from [Billboard.com](http://www.billboard.com/charts/).

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
>>> song.title
'Nice For What'
>>> song.artist
'Drake'
>>> song.weeks  # Number of weeks on chart
2
```

We can also `print` the entire chart:

```
>>> print(chart)
hot-100 chart from 2018-04-28
-----------------------------
1. 'Nice For What' by Drake
2. 'God's Plan' by Drake
3. 'Meant To Be' by Bebe Rexha & Florida Georgia Line
4. 'Psycho' by Post Malone Featuring Ty Dolla $ign
5. 'The Middle' by Zedd, Maren Morris & Grey
# ...
```

Guide
-----

### Downloading a chart

Use the `ChartData` constructor to download a chart:

```Python
ChartData(name, date=None, fetch=True, timeout=25)
```

The arguments are:

* `name` &ndash; The chart name, e.g. `'hot-100'` or `'pop-songs'`. You can browse the [Charts page](http://www.billboard.com/charts) on Billboard.com to find valid chart names; the URL of a chart will look like `http://www.billboard.com/charts/CHART-NAME` ([example](http://www.billboard.com/charts/artist-100)). Almost any chart should work; the only chart known not to work is `spotify-rewind`.
* `date` &ndash; The chart date as a string, in YYYY-MM-DD format. By default, the latest chart is fetched.
* `fetch` &ndash; A boolean indicating whether to fetch the chart data from Billboard.com immediately (at instantiation time). If `False`, the chart data can be populated at a later time using the `fetchEntries()` method.
* `timeout` &ndash; The number of seconds to wait for a server response. If `None`, no timeout is applied.

### Walking through chart dates

Every `ChartData` instance has a `previousDate` attribute containing a string representation of the previous chart's date. You can feed this into another `ChartData` instance to effectively walk back through previous charts.

```python
chart = billboard.ChartData('hot-100')
while chart.previousDate:
    doSomething(chart)
    chart = billboard.ChartData('hot-100', chart.previousDate)
``` 

### Accessing chart entries

If `chart` is a `ChartData` instance, we can ask for its `entries` attribute to get the chart entries (see below) as a list.

For convenience, `chart[x]` is equivalent to `chart.entries[x]`, and `ChartData` instances are iterable.

### Chart entry attributes

A chart entry (typically a single track) is of type `ChartEntry`. A `ChartEntry` instance has the following attributes:

* `title` &ndash; The title of the track.
* `artist` &ndash; The name of the artist, as formatted on Billboard.com.
* `peakPos` &ndash; The track's peak position on the chart at any point in time, including future dates, as an int (or `None` if the chart does not include this information).
* `lastPos` &ndash; The track's position on the previous week's chart, as an int (or `None` if the chart does not include this information). This value is 0 if the track was not on the previous week's chart.
* `weeks` &ndash; The number of weeks the track has been or was on the chart, including future dates (up until the present time).
* `rank` &ndash; The track's current position on the chart.
* `isNew` &ndash; Whether the track is new to the chart.

### More resources

For additional documentation, look at the file `billboard.py`, or use Python's interactive `help` feature.

Think you found a bug? Create an issue [here](https://github.com/guoguo12/billboard-charts/issues).

Contributing
------------

Pull requests are welcome! Please adhere to the following style guidelines:

* In general, follow [PEP 8](https://www.python.org/dev/peps/pep-0008/). You may ignore the following rules if following them would decrease readability:
    * E127 ("continuation line over-indented for visual indent")
    * E221 ("multiple spaces before operator")
    * E501 ("line too long")
* We use `mixedCase` for variable names.
* All-uppercase words remain all-uppercase when they appear at the end of variable names (e.g. `downloadHTML` not `downloadHtml`).

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

Made with billboard.py
------------
Projects and articles that use billboard.py:

* ["What Makes Music Pop?"](https://cs1951a2016millionsong.wordpress.com/2016/05/14/final-report/) by Zach Loery
* ["How Has Hip Hop Changed Over the Years?"](https://rohankshir.github.io/2016/02/28/topic-modeling-on-hiphop/) by Rohan Kshirsagar
* ["Spotify and billboard.py"](http://aguo.us/writings/spotify-billboard.html) by Allen Guo
* [chart_success.py](https://github.com/3ngthrust/calculate-chart-success-2/) by 3ngthrust
* ["Top Billboard Streaks"](https://twitter.com/polygraphing/status/748543281345224704) and ["Drake's Hot-100 Streak"](https://twitter.com/polygraphing/status/748987711541940224) by James Wenzel @ Polygraph
* ["Determining the 'Lifecycle' of Each Music Genre"](http://thedataface.com/genre-lifecycles/) by Jack Beckwith @ The Data Face
* ["Splunking the Billboard Hot 100 with Help from the Spotify API"](https://www.function1.com/2017/09/splunking-the-billboard-hot-100-with-help-from-the-spotify-api) by Karthik Subramanian
* ["Predicting Movement on 70s & 80s Billboard R&B Charts"](https://afriedman412.github.io/Predicting-Movement-On-70s-&-80s-Billboard-R&B-Charts/) by Andy Friedman

Have an addition? Make a pull request!

Dependencies
------------
* [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/)
* [Requests](http://requests.readthedocs.org/en/latest/) 

License
-------

* This project is licensed under the MIT License.
* The *Billboard* charts are owned by Prometheus Global Media LLC. See Billboard.com's [Terms of Use](http://www.billboard.com/terms-of-use) for more information.
