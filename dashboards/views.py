from django.conf import settings
from django.shortcuts import redirect
from metalayercore.dashboards.controllers import DashboardsController
from metalayercore.dashboards.models import DashboardShortUrl
from django.contrib import messages

def redirect_to_dashboard(request, url_id):
    short_url = DashboardShortUrl.Load(url_id)
    if not short_url:
        messages.error(request, 'The url you supplied could not be found')
        return redirect('http://%s' % settings.SITE_HOST)
    dashboard = DashboardsController.GetDashboardById(short_url.dashboard_id)
    return redirect('http://%s/delv/%s/%s' % (settings.SITE_HOST, dashboard['username'], dashboard['id']))