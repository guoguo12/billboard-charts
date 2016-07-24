billboard.py
============

[![Build Status](https://travis-ci.org/guoguo12/billboard-charts.svg)](https://travis-ci.org/guoguo12/billboard-charts)

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
u'One Dance'
>>> song.artist      # Get the artist
u'Drake Featuring WizKid & Kyla'
>>> song.weeks       # Get number of weeks on chart
15
```

We can also easily pretty-print the entire chart:

```Python
>>> print chart
```

which gives (as of July 23, 2016):

```
hot-100 chart (current)
-----------------------
1. 'One Dance' by Drake Featuring WizKid & Kyla (0)
2. 'Can't Stop The Feeling!' by Justin Timberlake (0)
3. 'Cheap Thrills' by Sia Featuring Sean Paul (+2)
4. 'This Is What You Came For' by Calvin Harris Featuring Rihanna (0)
5. 'Don't Let Me Down' by The Chainsmokers Featuring Daya (-2)
6. 'Ride' by twenty one pilots (+2)
7. 'Needed Me' by Rihanna (0)
8. 'Panda' by Desiigner (-2)
9. 'Don't Mind' by Kent Jones (0)
10. 'Send My Love (To Your New Lover)' by Adele (+2)
# ... 90 more lines
```

Full documentation
------------------

### Downloading a chart

Use the `ChartData` constructor to download a chart:

```Python
ChartData(name, date=None, fetch=True, all=False, quantize=True)
```

The arguments are:

* `name` &ndash; The chart name, e.g. `'hot-100'` or `'pop-songs'`. You can browse the Charts section of Billboard.com to find valid chart names; the URL of a chart will look like `http://www.billboard.com/charts/CHART-NAME` ([example](http://www.billboard.com/charts/artist-100)).
* `date` &ndash; The chart date as a string, in YYYY-MM-DD format. By default, the latest chart is fetched.
* `fetch` &ndash; A boolean indicating whether to fetch the chart data from Billboard.com immediately (at instantiation time). If `False`, the chart data can be populated at a later time using the `fetchEntries()` method.
* `all` &ndash; Deprecated; has no effect.
* `quantize` &ndash; A boolean indicating whether to round the `date` parameter to the nearest date with a chart.

### Walking through chart dates

Every `ChartData` instance has a `previousDate` attribute containing a string representation of the previous chart's date. You can feed this into another `ChartData` instance to effectively walk back through previous charts.

```python
from time import sleep

import billboard

chart = billboard.ChartData('hot-100')
while chart.previousDate:
    doSomething(chart)
    chart = billboard.ChartData('hot-100', chart.previousDate)
    sleep(2)  # Throttle requests
``` 

### Accessing chart entries

If `chart` is a `ChartData` instance, we can ask for its `entries` attribute to get the chart entries (see below) as a list.

For convenience, `chart[x]` is equivalent to `chart.entries[x]`, and `ChartData` instances are iterable.

### Chart entry attributes

A chart entry (typically a single track) is of type `ChartEntry`. A `ChartEntry` instance has the following attributes:

* `title` &ndash; The title of the track.
* `artist` &ndash; The name of the artist, as formatted on Billboard.com. If there are multiple artists and/or featured artists, they will all be included in this string.
* `peakPos` &ndash; The track's peak position on the chart, as an int.
* `lastPos` &ndash; The track's position on the previous week's chart, as an int. This value is 0 if the track has never been on the chart before.
* `weeks` &ndash; The number of weeks the track has been on the chart. This value is 1 if the track is new on the chart.
* `rank` &ndash; The track's current position on the chart.
* `change` &ndash; A string indicating how the track's position has changed since the previous week. This may be one of the following:
  * A signed integer like +4, -1, or 0, indicating the difference between the track's current position and its position on the previous week's chart.
  * 'Hot Shot Debut', which means track is the highest-rated track that is completely new to the chart.
  * 'New', which means the track is completely new to the chart, yet not the highest rated new track.
  * 'Re-Entry', which means the track is re-entering the chart after leaving it for at least a week.
* `spotifyID` &ndash; The Spotify ID of the track, or an empty string if it was not provided. This can be used to access more information about the track via the [Spotify Web API](https://developer.spotify.com/web-api/get-tr ack/).
* `spotifyLink` &ndash; The Spotify embed URL of the track, generated from the spotifyID. Will be an empty string if no such ID was provided.
* `videoLink` &ndash; The video URL of the track. Will be an empty string if no such URL was provided.



### More resources

For additional documentation, take a look at the source code for `billboard.py`, or use Python's interactive `help` feature.

If you're stuck or confused: This is a small project, so you can also just email me (Allen). My contact info is on my profile page.

Contributing
------------

Found a bug? Create an issue [here](https://github.com/guoguo12/billboard-charts/issues).

Pull requests are welcome! Please adhere to the following style guidelines:

* In general, follow [PEP 8](https://www.python.org/dev/peps/pep-0008/). You may ignore E501 ("line too long") and E127 ("continuation line over-indented for visual indent") if following them would detract from the readability of the code. Use your best judgement!
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
* ["Top Billboard Streaks"](https://twitter.com/polygraphing/status/748543281345224704) and ["Drake's Hot-100 Streak"](https://twitter.com/polygraphing/status/748987711541940224) by James Wenzel @ Polygraph

Have an addition? Make a pull request!

Dependencies
------------
* [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/)
* [Requests](http://requests.readthedocs.org/en/latest/) 

License
-------

* This project is licensed under the MIT License.
* The *Billboard* charts are owned by Prometheus Global Media LLC. See Billboard.com's [Terms of Use](http://www.billboard.com/terms-of-use) for more information.
