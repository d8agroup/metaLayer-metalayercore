from django.conf.urls.defaults import patterns, url
from metalayercore.dashboards.views import *

urlpatterns = patterns('',
    url(r'(\w+)', redirect_to_dashboard),
)