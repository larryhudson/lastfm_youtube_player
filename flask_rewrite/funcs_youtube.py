import requests
from os import environ
import json
from fuzzywuzzy import fuzz

def compare_song_vid(song_string, vid_string):
    fuzz_ratio = fuzz.token_sort_ratio(song_string, vid_string)

    print("Fuzz ratio:", str(fuzz_ratio))
    if fuzz_ratio > 80:
        return True
    else:
        return False

def get_playlist_vids(playlist_id):

    youtube_key = environ['YOUTUBE_KEY']
    request_url = "https://www.googleapis.com/youtube/v3/" \
                + "playlistItems?" \
                + "part=snippet" \
                + "&maxResults=50" \
                + "&playlistId=" + playlist_id \
                + "&key=" + youtube_key

    plist_vids_dict = json.loads(requests.get(request_url).text)

    playlist_vids = [{'id': video['snippet']['resourceId']['videoId'],
                             'title': video['snippet']['title']}
                            for video in plist_vids_dict['items']]

    return playlist_vids


def playlist_search(artist, album):
    search_string = artist + " " + album
    youtube_key = environ['YOUTUBE_KEY']
    search_url = "https://www.googleapis.com/youtube/v3/search" \
               + "?part=snippet&type=playlist&q=" + search_string \
               + "&key=" + youtube_key
    playlist_search_dict = json.loads(requests.get(search_url).text)

    plist_search_results = [{'id': result['id']['playlistId'],
                             'title': result['snippet']['title']}
                            for result in playlist_search_dict['items']]

    for plist in plist_search_results:
        if compare_song_vid(search_string, plist['title']):
            plist_songs = get_playlist_vids(plist['id'])

    return False


def keyword_search(artist, album, track):
    song_string = artist + " " + track
    youtube_key = environ['YOUTUBE_KEY']
    request_url = "https://www.googleapis.com/youtube/v3/search" \
                + "?part=snippet&type=video&q=" + song_string \
                + "&key=" + youtube_key

    keyword_search_dict = json.loads(requests.get(request_url).text)
    json_dict_results = keyword_search_dict['items']

    search_results = [{'id': result['id']['videoId'],
                       'title': result['snippet']['title']}
                          for result in json_dict_results]

    for item in search_results:

        if compare_song_vid(song_string, item['title']):
            match_id = item['id']
            print("Assigned video id", match_id, "to", song_string, "from keyword search")
            return match_id

        secondary_song_string = artist + " " + album + " " + track

        if compare_song_vid(secondary_song_string, item['title']):
            match_id = item['id']
            return match_id
