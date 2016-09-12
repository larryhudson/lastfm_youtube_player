import xmltodict
import requests
from os import environ


def album_search(artist, album):
    method = "album.getinfo"
    lastfm_key = environ["LASTFM_KEY"]
    request_url = "http://ws.audioscrobbler.com/2.0/?" \
                + "method=" + method \
                + "&artist=" + artist \
                + "&album=" + album \
                + "&api_key=" + lastfm_key

    r = requests.get(request_url)
    xml_dict = xmltodict.parse(r.text)

    xml_tracks = xml_dict['lfm']['album']['tracks']['track']

    album = {}
    album['info'] = {'artist': xml_dict['lfm']['album']['artist'],
                     'name': xml_dict['lfm']['album']['name'],
                     }

    album['tracks'] = [{'num': track['@rank'], 'name': track['name'], 'video_id': False}
                       for track in xml_tracks]

    return album
