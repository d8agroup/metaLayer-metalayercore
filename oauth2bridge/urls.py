from django.conf.urls.defaults import patterns, url
from views import handle_google_oauth2_callback, handle_facebook_oauth2_callback

urlpatterns = patterns('',
    url(r'google_oauth2_callback$', handle_google_oauth2_callback),
    url(r'facebook_oauth2_callback$', handle_facebook_oauth2_callback),
)
