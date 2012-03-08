from django.http import Http404, HttpResponse
from metalayercore.dashboards.controllers import DashboardsController
from logger import Logger
from metalayercore.outputs.controllers import OutputController
from metalayercore.outputs.models import ShortUrl
from metalayercore.search.controllers import SearchController

def generate_output(request, url_identifier):
    Logger.Info('%s - generate_output - started' % __name__)
    Logger.Debug('%s - generate_output - started with url_identifier:%s' % (__name__, url_identifier))
    short_url = ShortUrl.Load(url_identifier)
    if not short_url:
        Logger.Error('%s - generate_output - error - url_identifier:%s not found' % (__name__, url_identifier))
        Logger.Info('%s - generate_output - finished' % __name__)
        raise Http404
    dashboard_id = short_url.dashboard_id
    collection_id = short_url.collection_id
    output_id = short_url.output_id
    dashboard = DashboardsController.GetDashboardById(dashboard_id)
    if not dashboard:
        Logger.Error('%s - generate_output - error - dashboard_id:%s not found' % (__name__, dashboard_id))
        Logger.Info('%s - generate_output - finished' % __name__)
        raise Http404
    collection = None
    for c in dashboard.collections:
        if c['id'] == collection_id:
            collection = c
            break
    if not collection:
        Logger.Error('%s - generate_output - error - collection_id:%s not found' % (__name__, collection_id))
        Logger.Info('%s - generate_output - finished' % __name__)
        raise Http404
    output = None
    if 'outputs' in collection:
        for o in collection['outputs']:
            if o['id'] == output_id:
                output = o
                break
    if not output:
        Logger.Error('%s - generate_output - error - output_id:%s not found' % (__name__, output_id))
        Logger.Info('%s - generate_output - finished' % __name__)
        raise Http404
    sc = SearchController(collection)
    search_results = sc.run_search_and_return_results()
    oc = OutputController(output)
    content, content_type = oc.generate_output(search_results)
    Logger.Info('%s - generate_output - finished' % __name__)
    response = HttpResponse(content=content, content_type=content_type)
    response['Access-Control-Allow-Origin'] = '*'
    return response
