# Example: Top Singles Playlist

**Note: This example no longer works, as of [#22](https://github.com/guoguo12/billboard-charts/pull/22).**

In this example, we'll create a Spotify playlist containing the past 100 songs that have reached the top spot on the Hot 100. We'll be using billboard.py and [Spotipy](https://spotipy.readthedocs.org/), which is a wrapper around the [Spotify Web API](https://developer.spotify.com/web-api/).

To view the example, see `run.py`.

## Overview

[This blog post](http://aguo.us/writings/spotify-billboard.html) provides a good overview of how this example works.

The actual `run.py` features several minor improvements over the version described in the blog post:

* More error-handling.
* More variables have been made constants.
* billboard.py requests are throttled.

## Instructions

To run this example, create a [Spotify Developer](https://developer.spotify.com) account. (You'll need a regular Spotify account to do so.) Register an app with the Spotify API, then fill out the first three constants at the top of `run.py`:

```python
SPOTIFY_USERNAME      = 'YOUR_SPOTIFY_USERNAME'
SPOTIFY_CLIENT_ID     = 'YOUR_CLIENT_ID'
SPOTIFY_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
```

Make any necessary adjustments to the other constants before proceeding.

The first time you run the script, you'll have to authorize the app you made to create playlists on your behalf. Follow the instructions in your terminal.

If you have any questions, or if you find a bug, feel free to create a new issue.
