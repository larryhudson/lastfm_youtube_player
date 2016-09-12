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
            return match_id

        secondary_song_string = artist + " " + album + " " + track

        if compare_song_vid(secondary_song_string, item['title']):
            match_id = item['id']
            return match_id





    return 0
