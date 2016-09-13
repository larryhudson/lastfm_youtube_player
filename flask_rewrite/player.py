from flask import Flask, render_template, request
import funcs_lastfm as lfm
import funcs_youtube as yt

app = Flask(__name__)


@app.route('/album/<artist_slug>/<album_slug>')
def play_album(artist_slug, album_slug):
    artist_input = artist_slug.replace("-", " ")
    album_input = album_slug.replace("-", " ")
    album = lfm.album_search(artist_input, album_input)

    # try playlist search
    yt.playlist_search(album)

    # keyword search for remaining tracks
    for track in album['tracks']:
        if not track['video_id']:
            track['video_id'] = yt.keyword_search(artist=album['info']['artist'],
                                                  album=album['info']['name'],
                                                  track=track['name'])

    return render_template("album2.html", album=album)

@app.route('/search_tag/<tag_slug>')
def search_tag(tag_slug):
    tag_input = tag_slug.replace("-"," ")
    albums = lfm.albums_with_tag(tag_input)
    search_string = "Top albums for tag: " + tag_input
    return render_template("result.html", albums=albums)
