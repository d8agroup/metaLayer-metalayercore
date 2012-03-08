from django.conf import settings
from django.shortcuts import redirect
from dashboard.constants import USER_MESSAGES
from metalayercore.dashboards.controllers import DashboardsController
from metalayercore.dashboards.models import DashboardShortUrl
from django.contrib import messages

def redirect_to_dashboard(request, url_id):
    short_url = DashboardShortUrl.Load(url_id)
    if not short_url:
        messages.error(request, USER_MESSAGES['short_url_not_round'])
        return redirect('http://%s' % settings.SITE_HOST)
    dashboard = DashboardsController.GetDashboardById(short_url.dashboard_id)
    return redirect('http://%s/delv/%s/%s' % (settings.SITE_HOST, dashboard['username'], dashboard['id']))