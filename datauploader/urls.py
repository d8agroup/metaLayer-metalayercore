from django.conf.urls.defaults import patterns, url
from views import return_uploaders_that_can_parse_file, process_file_with_datauploader

urlpatterns = patterns('',
    url(r'file_from_dashboard$', return_uploaders_that_can_parse_file),
    url(r'process_file_with_datauploader', process_file_with_datauploader)
)