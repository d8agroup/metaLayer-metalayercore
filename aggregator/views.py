from django.views.decorators.csrf import csrf_exempt
from metalayercore.aggregator.controllers import AggregationController
from django.utils import simplejson as json
from logger import Logger
from utils import  JSONResponse, async

@async
def run_all_dashboards(request):
    Logger.Info('%s - run_all_dashboards - started' % __name__)
    user_filter = request.GET.get('user_filter')
    Logger.Debug('%s - run_all_dashboards - running with user_filter: %s' % (__name__, user_filter))
    yield JSONResponse({'status':'success'})
    aggregator = AggregationController(user_filter)
    aggregator.aggregate()
    Logger.Info('%s - run_all_dashboards - finished' % __name__)

@csrf_exempt
def post_content(request):
    content = request.POST.get('content')
    if not content:
        Logger.Warn('%s - post_content - no content supplied in POST body' % __name__)
        return JSONResponse({'status':'error', 'errors':['No content supplied in POST field']})
    try:
        content = json.loads(content)
    except Exception, e:
        Logger.Warn('%s - post_content - error while decoding json content in POST body' % __name__)
        Logger.Debug('%s - post_content - error while decoding json content in POST body: %s' % (__name__, e))
        return JSONResponse({'status':'error', 'errors':['There was an error json decoding the POST field "content"']})

    actions = request.POST.get('actions')
    if actions:
        try:
            actions = json.loads(actions)
        except Exception, e:
            Logger.Warn('%s - post_content - error while decoding json actions in POST body' % __name__)
            Logger.Debug('%s - post_content - error while decoding json actions in POST body: %s' % (__name__, e))
            return JSONResponse({'status':'error', 'errors':['There was an error json decoding the POST field "actions"']})

    skip_duplicate_check = request.POST.get('skip_duplicate_check')
    skip_duplicate_check = True if skip_duplicate_check and skip_duplicate_check == 'true' else False

    if not (AggregationController.AggregateUploadedContent(content, actions, skip_duplicate_check)):
        return JSONResponse({'status':'error', 'errors':['There was an error running the post content system']})

    return JSONResponse({'status':'success'})

