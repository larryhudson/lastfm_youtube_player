import requests
import json
import xmltodict
import aniso8601
from fuzzywuzzy import fuzz
from .models import Album, Song
from django.utils.text import slugify
from django.conf import settings

lastfm_key = settings.LASTFM_KEY
youtube_key = settings.YOUTUBE_KEY

def album_search(artist_input, album_input):
	method = "album.getinfo"
	request_url = "http://ws.audioscrobbler.com/2.0/?" \
	            + "method=" + method \
				+ "&artist=" + artist_input \
	            + "&album=" + album_input \
	            + "&api_key=" + lastfm_key

	r = requests.get(request_url)
	xml_dict = xmltodict.parse(r.text)
	
	album_object = Album()
	
	album_object.artist = xml_dict['lfm']['album']['artist']
	album_object.name = xml_dict['lfm']['album']['name']
	album_object.slug = slugify(album_object.artist + " " + album_object.name)
	if 'wiki' in xml_dict['lfm']['album']:
		album_object.summary = xml_dict['lfm']['album']['wiki']['summary']
	album_object.num_tracks = len(xml_dict['lfm']['album']['tracks']['track'])
	album_object.save()
	
	for track in xml_dict['lfm']['album']['tracks']['track']:
		track_object = Song(album_id=album_object.id)
		track_object.track_num = int(track['@rank'])
		track_object.name = track['name']
		track_object.artist = album_object.artist
		if 'duration' in track:
			track_object.duration = track['duration']
		else:
			track_object.duration = False
		track_object.save()
# 	
	return album_object
	# inside xml_dict['lfm']['album']
    # release date ['releasedate']
    # ['image size='medium']
    # ['tracks']['track'][0], etc.
         # ['@rank="1"']
	     # ['duration']


def get_duration_dict(id_list):
	
	id_string = ','.join(id_list)
	
	request_url = "https://www.googleapis.com/youtube/v3/videos?" \
	            + "part=contentDetails" \
				+ "&maxResults=50" \
				+ "&id=" + id_string \
				+ "&key=" + youtube_key
	durations_request = requests.get(request_url)
	durations_data = json.loads(durations_request.text)
	durations_dict = {}
	for item in durations_data['items']:
		duration = aniso8601.parse_duration(item['contentDetails']['duration']).seconds
		id = item['id']
		durations_dict[id] = duration
	
	return durations_dict

def get_single_duration(id):
	
	request_url = "https://www.googleapis.com/youtube/v3/videos?" \
	            + "part=contentDetails" \
				+ "&maxResults=50" \
				+ "&id=" + id \
				+ "&key=" + youtube_key
	durations_request = requests.get(request_url)
	durations_data = json.loads(durations_request.text)
	duration = aniso8601.parse_duration(durations_data['items'][0]['contentDetails']['duration']).seconds
	
	return duration	 
	
def list_playlist_vids(playlist_id):
	
	request_url = "https://www.googleapis.com/youtube/v3/" \
	            + "playlistItems?" \
				+ "part=snippet" \
				+ "&maxResults=50" \
				+ "&playlistId=" + playlist_id \
				+ "&key=" + youtube_key
	
	playlist_items_request = requests.get(request_url)
	playlist_items_dict = json.loads(playlist_items_request.text)
	playlist_vids = []
	vid_num = 1
	
	for vid in playlist_items_dict['items']:
		id = vid['snippet']['resourceId']['videoId']
		title = vid['snippet']['title']
		playlist_vids.append([vid_num, id, title])
		vid_num += 1
	
	playlist_vid_ids = []
	for item in playlist_vids:
		id = item[1]
		playlist_vid_ids.append(id)
	
# 	vid_duration = get_duration_dict(playlist_vid_ids)
# 	
# 	for video in playlist_vids:
# 		vid_id = video[1]
# 		duration = vid_duration[vid_id]
# 		video.append(duration)
		
	# [vid_num, id, title, duration]	
	return playlist_vids

def compare_song_vid(song, vid):
	# vid should be a list of [vid_num, video_id, vid_name
	song_string = song.artist + " - " + song.name
	vid_name = vid[2]
	
	fuzz_ratio = fuzz.token_sort_ratio(song_string, vid_name)
	
	print("Fuzz ratio:", str(fuzz_ratio))
	if fuzz_ratio > 80:
		print("We've got a match!")
		return True
	else:
		print("Titles not close enough.")
		return False

def keyword_search(song):
	song_string = song.artist + " " + song.name
	keyword_search_request = requests.get("https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q=" + song_string + "&key=" + youtube_key)
	keyword_search_dict = json.loads(keyword_search_request.text)
	
	search_results = []
	for item in keyword_search_dict['items']:
		vid_num = 0
		video_id = item['id']['videoId']
		vid_name = item['snippet']['title']
		search_results.append([vid_num, video_id, vid_name])
	
	done = False
	
	for item in search_results:
		if compare_song_vid(song, item):
			match_id = item[1]
			return match_id
		
	return 0
	
def get_playlist(album):
	album_string = album.artist + " " + album.name
	playlist_search_request = requests.get("https://www.googleapis.com/youtube/v3/search?part=snippet&type=playlist&q=" + album_string + "&key=" + youtube_key)
	playlist_search_dict = json.loads(playlist_search_request.text)
	playlists_list = []
	for item in playlist_search_dict['items']:
		id = item['id']['playlistId']
		title = item['snippet']['title']
		if fuzz.token_sort_ratio(album_string, title) > 80:
			playlists_list.append([id, title])
	
	skip_playlist = False
	
	try:
		playlist_vids_list = list_playlist_vids(playlists_list[0][0])
	except IndexError:
		skip_playlist = True
	
	album_tracklist = Song.objects.filter(album=album)
	if not skip_playlist:
		for vid in playlist_vids_list:
			vid_num = vid[0]
			for song in album_tracklist:
				track_num = song.track_num
				if vid_num == track_num:
					if compare_song_vid(song, vid):
						song.save()
	
	still_no_vid = album_tracklist.filter(youtube_link=0)
	
	for song in still_no_vid:
		song.youtube_link = keyword_search(song)
		song.save()
	
	return playlists_list
	