from metalayercore.aggregator.controllers import AggregationController
from logger import Logger
from utils import  JSONResponse

#@async
def run_all_dashboards(request):
    Logger.Info('%s - run_all_dashboards - started' % __name__)
    user_filter = request.GET.get('user_filter')
    Logger.Debug('%s - run_all_dashboards - running with user_filter: %s' % (__name__, user_filter))
    aggregator = AggregationController(user_filter)
    aggregator.aggregate()
    Logger.Info('%s - run_all_dashboards - finished' % __name__)
    return JSONResponse({'status':'success'})

