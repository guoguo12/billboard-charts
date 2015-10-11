billboard.py
============

**billboard.py** is a Python API for accessing ranking charts from Billboard.com.

Quick start
-----------

To download a *Billboard* chart, we use the `ChartData()` constructor.

Let's fetch the current [Hot 100](http://www.billboard.com/charts/hot-100) chart.

```Python
>>> import billboard
>>> chart = billboard.ChartData('hot-100')
```

Now we can manipulate the chart entries, which are of type `ChartEntry` and have attributes like `artist`, `title`, and `album`:

```Python
>>> song = chart[0]  # Get no. 1 song on chart
>>> song.artist
u'The Weeknd'
>>> song.title
u'The Hills'
>>> song.weeks       # Get no. of weeks on chart
19
>>> print song
'The Hills' by The Weeknd
```

We can also easily pretty-print the entire chart with:

```Python
print chart
```

which as of 11 October 2015 gives:

```
hot-100 chart (current)
-----------------------
1. 'The Hills' by The Weeknd (0)
2. 'What Do You Mean?' by Justin Bieber (0)
3. 'Hotline Bling' by Drake (+1)
4. 'Can't Feel My Face' by The Weeknd (-1)
5. '679' by Fetty Wap Featuring Remy Boyz (+1)
6. 'Locked Away' by R. City Featuring Adam Levine (+1)
7. 'Watch Me' by Silento (-2)
8. 'Wildest Dreams' by Taylor Swift (+2)
9. 'Stitches' by Shawn Mendes (+2)
10. 'Good For You' by Selena Gomez Featuring A$AP Rocky (-2)
# ... 90 more lines
```

Dependencies
------------
* [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/)
* [Requests](http://requests.readthedocs.org/en/latest/) 

License
-------

* This project is licensed under the MIT License.
* The *Billboard* charts are owned by Prometheus Global Media LLC. See Billboard.com's [Terms of Use](http://www.billboard.com/terms-of-use) for more information.
