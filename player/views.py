from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from .models import Album, Song
from . import lastfm_search as lfm
from .forms import SearchForm
from django.utils.text import slugify 

def index(request):
	# show recently added albums
	context = {'name': name}
	return render(request, "index.html", context)

def detail(request, slug):
	album = get_object_or_404(Album, slug=slug)
	track_list = Song.objects.filter(album=album)     
	return render(request, 'detail.html', {'album':album, 'tracklist':track_list})

def search(request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = SearchForm(request.POST)
		# check whether it's valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required
			user_artist = form.cleaned_data['artist_input']
			user_album = form.cleaned_data['album_input']
			search_slug = slugify(user_artist + " " + user_album)
			try:
				album_object = Album.objects.get(slug=search_slug)
			except Album.DoesNotExist:
				album_object = lfm.album_search(user_artist, user_album)
				lfm.get_playlist(album_object)
			# redirect to a new URL:
			return redirect("player:detail", slug=album_object.slug)
	# if a GET (or any other method) we'll create a blank form
	else:
		form = SearchForm()

	return render(request, 'search.html', {'form': form})





