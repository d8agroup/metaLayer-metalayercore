from django.conf.urls.defaults import patterns, url
from metalayercore.outputs.views import *

urlpatterns = patterns('',
    url(r'(\w+)', generate_output),
)