from django.db import models

class Album(models.Model):
	name = models.CharField(max_length=25, default="Unknown album")
	artist = models.CharField(max_length=50, default="Unknown artist")
	slug = models.SlugField(max_length=50)
	year_released = models.IntegerField(default=0)
	num_tracks = models.IntegerField(default=0)
	total_duration = models.IntegerField(default=0)
	summary = models.CharField(max_length=500, default="No info available")
	
	def __str__(self):
		return str(self.artist) + " - " + str(self.name)
	
class Song(models.Model):
	name = models.CharField(max_length=50, default="Song title")
	artist = models.CharField(max_length=50, default="Unknown artist")
	album = models.ForeignKey(Album,on_delete=models.CASCADE)
	slug = models.SlugField(max_length=50, default="slug")
	track_num = models.IntegerField(default=0)
	youtube_link = models.URLField(default=0)
	duration = models.IntegerField(default=0)
	
	def __str__(self):
		return str(self.artist) + " - " + str(self.name)
		
	@property
	def next_song(self):
		
		return 
	
	
