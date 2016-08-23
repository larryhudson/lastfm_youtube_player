from django.contrib import admin

from .models import Album, Song

# Register your models here.

# Prepopulate fields
class AlbumAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("artist","name",)}

admin.site.register(Album, AlbumAdmin)
admin.site.register(Song)

