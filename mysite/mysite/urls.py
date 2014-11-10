from django.conf.urls import patterns, include, url
from django.contrib import admin
from views import *

urlpatterns = patterns('',
    url(r'^$', hello),
    url(r'^admin/', include(admin.site.urls)),
)
