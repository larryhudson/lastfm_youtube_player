from flask import Flask, render_template, request
import funcs_lastfm as lfm
import funcs_youtube as yt

app = Flask(__name__)


@app.route('/album/<artist_slug>/<album_slug>')
def play_album(artist_slug, album_slug):
    artist_input = artist_slug.replace("-", " ")
    album_input = album_slug.replace("-", " ")
    album = lfm.album_search(artist_input, album_input)

    for track in album['tracks']:

        track['video_id'] = yt.keyword_search(artist=album['info']['artist'],
                                              album=album['info']['name'],
                                              track=track['name'])

    return render_template("album.html", album=album)