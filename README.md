billboard.py
============

**billboard.py** is a Python API for accessing ranking charts from Billboard.com.

Quick Start
-----------

Let's fetch the current [Hot 100](http://www.billboard.com/charts/hot-100) chart.

```Python
>>> import billboard
>>> chart = billboard.ChartData('hot-100')
```

As of 8 December 2013, printing `chart` gives:
```
hot-100 chart (current)
-----------------------
1. 'Wrecking Ball' by Miley Cyrus from 'Bangerz [Deluxe Edition]'
2. 'The Monster' by Eminem Featuring Rihanna from 'The Marshall Mathers LP 2'
3. 'Royals' by Lorde from 'Pure Heroine'
4. 'Timber' by Pitbull Featuring Ke$ha
5. 'Counting Stars' by OneRepublic from 'Native'
6. 'Wake Me Up!' by Avicii from 'Wake Me Up'
7. 'Demons' by Imagine Dragons from 'Night Visions [Deluxe Edition]'
8. 'Story Of My Life' by One Direction from 'Story of My Life'
9. 'Roar' by Katy Perry from 'Prism [Deluxe Edition]'
10. 'Say Something' by A Great Big World & Christina Aguilera
```

Dependencies
------------
* [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/)
* [Requests](http://requests.readthedocs.org/en/latest/) 

License
-------

* This project is licensed under the MIT License.
* The *Billboard* charts are owned by Prometheus Global Media LLC. See Billboard.com's [Terms of Use](http://www.billboard.com/terms-of-use) for more information.
