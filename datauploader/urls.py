from django.conf.urls.defaults import patterns, url
from views import return_uploaders_that_can_parse_file, process_file_with_datauploader, get_content_item_template
from views import get_all_templates_with_options

urlpatterns = patterns('',
    url(r'get_all_templates_with_options$', get_all_templates_with_options),
    url(r'file_from_dashboard$', return_uploaders_that_can_parse_file),
    url(r'process_file_with_datauploader', process_file_with_datauploader),
    url(r'get_content_item_template/(\w+)', get_content_item_template),
)