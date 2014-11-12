from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import *

urlpatterns = patterns('',
    url(r'^$', hello),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^reporter/$', reporter),
    url(r'^mapper/$', mapper),
    url(r'^time_search_form/$', time_search_form),
    url(r'^time_search_results/$', time_search_results),
)
