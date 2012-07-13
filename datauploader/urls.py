from django.conf.urls.defaults import patterns, url
from views import file_upload_from_dashboard

urlpatterns = patterns('',
    url(r'file_from_dashboard$', file_upload_from_dashboard),
)