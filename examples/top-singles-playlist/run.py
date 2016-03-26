import sys
import time

import billboard
import spotipy
import spotipy.util

SPOTIFY_USERNAME      = 'YOUR_SPOTIFY_USERNAME'
SPOTIFY_CLIENT_ID     = 'YOUR_CLIENT_ID'
SPOTIFY_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
SPOTIFY_REDIRECT_URI  = 'https://github.com/guoguo12/billboard-charts'
SPOTIFY_SCOPE         = 'playlist-modify-public'

PLAYLIST_NAME = 'Best of the Hot 100'
TRACK_COUNT   = 100
CHART         = 'hot-100'
START_DATE    = None  # None for default (latest chart)
THROTTLE_TIME = 0.50  # Seconds


def unique_top_tracks_generator():
    seen_tracks = set()
    chart = billboard.ChartData(CHART, date=START_DATE)

    while len(seen_tracks) < TRACK_COUNT:
        top_track = chart[0]
        duplicate = top_track.spotifyLink in seen_tracks

        if not duplicate:
            seen_tracks.add(top_track.spotifyLink)
            yield top_track

        if not chart.previousDate:
            break
        time.sleep(THROTTLE_TIME)
        chart = billboard.ChartData(CHART, date=chart.previousDate)

    raise StopIteration


def main():
    token = spotipy.util.prompt_for_user_token(
        SPOTIFY_USERNAME,
        scope=SPOTIFY_SCOPE,
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI)
    if not token:
        sys.exit('Authorization failed')
    sp = spotipy.Spotify(auth=token)

    playlist = sp.user_playlist_create(SPOTIFY_USERNAME, PLAYLIST_NAME)
    playlist_id = playlist[u'id']

    for track in unique_top_tracks_generator():
        print track
        url = track.spotifyLink
        try:
            sp.user_playlist_add_tracks(SPOTIFY_USERNAME, playlist_id, [url])
        except Exception as e:
            print e


if __name__ == '__main__':
    main()
