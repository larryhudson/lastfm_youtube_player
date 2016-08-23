from django.conf.urls import url

from . import views

app_name = 'player'

urlpatterns = [
	url(r'^$', views.index, name="index"),
    url(r'^search/$', views.search, name="search"),
    url(r'^album/(?P<slug>[\w-]+)/$', views.detail, name="detail"),
]

# album/Ty+Segall/Twins