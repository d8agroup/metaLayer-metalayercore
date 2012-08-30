from django.http import HttpResponse
from metalayercore.oauth2bridge.controllers import (GoogleOauth2Controller,
    FacebookOauth2Controller)


def handle_google_oauth2_callback(request):
    GoogleOauth2Controller.HandleOauth2Return(request)
    return HttpResponse("""
        <html>
            <head>
                <script type='text/javascript' language='javascript'>
                    window.close()
                </script>
            </head>
        </html>
    """)


def handle_facebook_oauth2_callback(request):
    FacebookOauth2Controller.HandleOauth2Return(request)
    return HttpResponse("""
        <html>
            <head>
                <script type='text/javascript' language='javascript'>
                    window.close()
                </script>
            </head>
        </html>
    """)
