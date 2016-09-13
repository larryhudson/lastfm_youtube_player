import requests
from os import environ
import json
from fuzzywuzzy import fuzz

def compare_song_vid(song_string, vid_string, artist):
    if artist.lower() in song_string.lower() and artist.lower() in vid_string.lower():
        song_string = song_string.strip(artist)
        vid_string = vid_string.strip(artist)

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
                             'title': video['snippet']['title'],
                             'position': video['snippet']['position'],}
                            for video in plist_vids_dict['items']]
    sorted_playlist_vids = sorted(playlist_vids, key=lambda k: k['position'])
    return sorted_playlist_vids


def playlist_search(album_dict):
    search_string = album_dict['info']['artist'] + " - " + album_dict['info']['name']
    tracks = album_dict['tracks']
    artist_name = album_dict['info']['artist']
    youtube_key = environ['YOUTUBE_KEY']
    search_url = "https://www.googleapis.com/youtube/v3/search" \
               + "?part=snippet&type=playlist&q=" + search_string \
               + "&key=" + youtube_key
    playlist_search_dict = json.loads(requests.get(search_url).text)

    plist_search_results = [{'id': result['id']['playlistId'],
                             'title': result['snippet']['title'],
                             'channel': result['snippet']['channelTitle'],
                             }
                            for result in playlist_search_dict['items']]

    print(len(plist_search_results))

    found_plist = False
    for plist in plist_search_results:
        if plist['title'] == album_dict['info']['name'] \
        and plist['channel'] == (album_dict['info']['artist'] + " - Topic"):
            plist_songs = get_playlist_vids(plist['id'])
            found_plist = True

    if not found_plist:
        for plist in plist_search_results:
            if compare_song_vid(search_string, plist['title'], album_dict['info']['artist']):
                plist_songs = get_playlist_vids(plist['id'])
                found_plist = True
                break

    if found_plist:
        print("plist len:", str(len(plist_songs)), "album len:", str(len(tracks)))
        print(plist_songs)

        if len(plist_songs) == len(album_dict['tracks']):
            for video in plist_songs:
                done = False
                vid_name = video['title']
                clean_vid_name = vid_name.lower().strip("'!@#$.,")
                for song in tracks:
                    song_string = artist_name + " " + song['name']
                    clean_song_name = song['name'].lower().strip("'!@#$.,")
                    print("comparing", vid_name, "and", song_string)
                    if vid_name == song['name']:
                        song['video_id'] = video['id']
                        print("Assigned video id", video['id'], "to", song_string, "from playlist search")
                        done = True
                        break
                    if done:
                        continue
                    if clean_song_name in clean_vid_name:
                        song['video_id'] = video['id']
                        print("Assigned video id", video['id'], "to", song_string, "from playlist search")
                        done = True
                        break

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

        if compare_song_vid(song_string, item['title'], artist):
            match_id = item['id']
            print("Assigned video id", match_id, "to", song_string, "from keyword search")
            return match_id

        secondary_song_string = artist + " " + album + " " + track

        if compare_song_vid(secondary_song_string, item['title'], artist):
            match_id = item['id']
            return match_id
