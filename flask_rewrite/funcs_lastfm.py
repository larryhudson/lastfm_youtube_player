import xmltodict
import requests
import json
from os import environ


def album_search(artist, album):
    method = "album.getinfo"
    lastfm_key = environ["LASTFM_KEY"]
    request_url = "http://ws.audioscrobbler.com/2.0/?" \
                + "method=" + method \
                + "&artist=" + artist \
                + "&album=" + album \
                + "&api_key=" + lastfm_key \
                + "&format=json"

    json_dict = json.loads(requests.get(request_url).text)

    json_tracks = json_dict['album']['tracks']['track']

    album = {}
    album['info'] = {'artist': json_dict['album']['artist'],
                     'name': json_dict['album']['name'],
                     }

    album['tracks'] = [{'num': track['@attr']['rank'], 'name': track['name'], 'video_id': False}
                       for track in json_tracks]

    return album

def albums_with_tag(tag):
    method = "tag.getTopAlbums"
    lastfm_key = environ["LASTFM_KEY"]
    request_url = "http://ws.audioscrobbler.com/2.0/?" \
                + "method=" + method \
                + "&tag=" + tag \
                + "&api_key=" + lastfm_key \
                + "&format=json"

    json_dict = json.loads(requests.get(request_url).text)

    json_albums = json_dict['albums']['album']

    albums = [{'name': album['name'],
            'artist': album['artist']['name'],
            'image': album['image'][2]['#text'],
            'artist_slug': album['artist']['name'].lower().replace(" ", "-"),
            'album_slug': album['name'].lower().replace(" ", "-"),
              } for album in json_albums]

    return albums[:12]
