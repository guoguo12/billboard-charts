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
>>> chart.title
'The Hot 100'
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

### Listing all charts

Use the `charts` function to list all chart names:

```Python
>>> billboard.charts()
['hot-100', 'billboard-200', 'artist-100', 'social-50', ...
```

Alternatively, the bottom of [this page](https://www.billboard.com/charts) shows all charts grouped by category.

### Downloading a chart

Use the `ChartData` constructor to download a chart:

```Python
ChartData(name, date=None, fetch=True, timeout=25)
```

The arguments are:

* `name` &ndash; The chart name, e.g. `'hot-100'` or `'pop-songs'`.
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
* `image` &ndash; The URL of the image for the track.
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

* We use [Black](https://github.com/psf/black) for formatting.
  * If you have [pre-commit](https://pre-commit.com/) installed, run `pre-commit install` to install a pre-commit hook that runs Black.
* Variable names should be in `mixedCase`.

### Running tests

We use [Travis CI](https://travis-ci.org/guoguo12/billboard-charts) to automatically run our test suite on all PRs.

To run the test suite locally, install [nose](https://nose.readthedocs.org/en/latest/) and run

```
nosetests
```

To run the test suite locally on both Python 2.7 and 3.4, install [tox](https://tox.readthedocs.org/en/latest/) and run

```
tox
```

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
* ["Billboard Trends"](https://tom-johnson.net/2018/08/12/billboard-trends/) by Tom Johnson
* ["Billboard Charts Alexa Skill"](https://www.amazon.com/Cameron-Ezell-Billboard-Charts/dp/B07K5SX95L) by Cameron Ezell

Have an addition? Make a pull request!

Dependencies
------------
* [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/)
* [Requests](http://requests.readthedocs.org/en/latest/) 

License
-------

* This project is licensed under the MIT License.
* The *Billboard* charts are owned by Prometheus Global Media LLC. See Billboard.com's [Terms of Use](http://www.billboard.com/terms-of-use) for more information.
