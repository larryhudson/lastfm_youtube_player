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
    playlist_videos = yt.playlist_search(artist=album['info']['artist'], album=album['info']['name'])


    if playlist_videos:
        for track in album['tracks']:
            song_string = album['info']['artist'] + " " + track["name"]
            for playlist_vid in playlist_videos:
                if yt.compare_song_vid(song_string, playlist_vid['title']):
                    track['video_id'] = playlist_vid['id']
                    print("Assigned video id", track['video_id'], "to", song_string)

    for track in album['tracks']:
        if not track['video_id']:
            track['video_id'] = yt.keyword_search(artist=album['info']['artist'],
                                                  album=album['info']['name'],
                                                  track=track['name'])

    return render_template("album.html", album=album)
