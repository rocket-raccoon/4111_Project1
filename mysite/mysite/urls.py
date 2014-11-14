from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import *

urlpatterns = patterns('',
    url(r'^$', home_page),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^reporter/$', reporter),
    url(r'^mapper/$', mapper),
    url(r'^time_search_form/$', time_search_form),
    url(r'^time_search_results/$', time_search_results),
    url(r'^airline_leaderboard/$', airline_leaderboard),
    url(r'^location_search_form/$', location_search_form),
    url(r'^location_search_results/$', location_search_results),
    url(r'^flight_environment/$', flight_environment),
)
