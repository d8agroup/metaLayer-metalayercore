from django.conf.urls.defaults import patterns, url
from metalayercore.imaging.views import *

urlpatterns = patterns('',
    url(r'facebook/(?P<dashboard_id>\w{24})\.png$', crop),
    url(r'c/(?P<width>\d+)/(?P<height>\d+)/(?P<dashboard_id>\w{24})\.png$', crop),
    url(r's/(?P<max_width>\d+)/(?P<max_height>\d+)/(?P<dashboard_id>\w{24})\.png$', shrink),
    url(r's/(?P<max_width>\d+)/(?P<max_height>\d+)/(?P<dashboard_id>\w{24})/(?P<visualization_id>\w+)\.png$', shrink),
)