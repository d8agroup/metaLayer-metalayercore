from django.conf.urls.defaults import patterns, url
from metalayercore.aggregator.views import *

urlpatterns = patterns('',
    url(r'run_all_dashboards', run_all_dashboards),
)