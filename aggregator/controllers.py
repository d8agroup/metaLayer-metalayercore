from Queue import Queue
import threading
import urllib2
from django.conf import settings
from django.contrib.auth.models import User
from metalayercore.actions.controllers import ActionController
from metalayercore.aggregator.models import RunRecord
from metalayercore.dashboards.controllers import DashboardsController
from metalayercore.datapoints.controllers import DataPointController
from logger import Logger
from django.utils import simplejson as json

class AggregationController(object):
    def __init__(self, user_filter):
        Logger.Info('%s - AggregationController.__init__ - started' % __name__)
        Logger.Debug('%s - AggregationController.__init__ - started with user_filter %s' % (__name__, user_filter))
        try:
            from userprofiles.controllers import UserController
            self.users = UserController.GetAllUsers(user_filter)
        except ImportError:
            self.users = User.objects.all()
            if user_filter and 'usernames' in user_filter:
                self.users = [u for u in self.users if u.username in user_filter['usernames']]
        Logger.Info('%s - AggregationController.__init__ - finished' % __name__)

    def aggregate(self):
        Logger.Info('%s - AggregationController.aggregate - stated' % __name__)
        for user in self.users:
            all_data_points_with_actions = []
            dc = DashboardsController(user)
            for dashboard in dc.get_live_dashboard():
                for collection in dashboard['collections']:
                    actions = collection['actions']
                    for data_point in collection['data_points']:
                        all_data_points_with_actions.append({'data_point':data_point, 'actions':actions})
            if all_data_points_with_actions:
                for data_point_with_actions in all_data_points_with_actions:
                    run_aggregator_for_data_point(data_point_with_actions['data_point'], data_point_with_actions['actions'])
        #Threading removed
#        finished = 0
#        def producer(q, users):
#            for user in users:
#                thread = _UserThread(user)
#                thread.start()
#                q.put(thread, True)
#        def consumer(q, users_count):
#            while finished <= users_count:
#                thread = q.get(True)
#                thread.join()
#                finished += 1
#        q = Queue(1)
#        producer_thread = threading.Thread(target=producer, args=(q, self.users))
#        consumer_thread = threading.Thread(target=consumer, args=(q, len(self.users)))
#        producer_thread.start()
#        consumer_thread.start()
        Logger.Info('%s - AggregationController.aggregate - finished' % __name__)

    @classmethod
    def AggregateUploadedContent(cls, content, actions, skip_duplicate_check=False):
        try:
            if skip_duplicate_check:
                apply_actions_and_post_to_solr(actions, content, False)
            else:
                apply_actions_and_post_to_solr(actions, content)
        except Exception, e:
            Logger.Error('%s - post_content - error posing content' % __name__)
            Logger.Debug('%s - post_content - error posing content: %s' % (__name__, e))
            return False
        return True

    @classmethod
    def AggregateSingleDataPoint(cls, data_point, actions=None):
        Logger.Info('%s - AggregationController.AggregateSingleDataPoint - started' % __name__)
        Logger.Debug('%s - AggregationController.AggregateSingleDataPoint - started with data_point: %s and actions:%s' % (__name__, data_point, actions))
        run_aggregator_for_data_point(data_point, actions)
        Logger.Info('%s - AggregationController.AggregateSingleDataPoint - finished' % __name__)

    @classmethod
    def AggregateMultipleDataPointHistoryWithAction(cls, action, data_points, historic_limit):
        Logger.Info('%s - AggregationController.AggregateMultipleDataPointHistoryWithAction - started' % __name__)
        Logger.Debug('%s - AggregationController.AggregateMultipleDataPointHistoryWithAction - started with action:%s and data_point:%s and historic_limit:%s' % (__name__, action, data_points, historic_limit))
        for data_point in data_points:
            dpc = DataPointController(data_point)
            solr_url = settings.SOLR_CONFIG['solr_url']
            solr_url = '%s/select/?q=*:*&wt=json&sort=time+desc&rows=%i&fq=source_id:%s' % (solr_url, historic_limit, dpc.generate_configured_guid())
            try:
                request = urllib2.Request(solr_url)
                response = urllib2.urlopen(request)
                response = json.loads(response.read())
            except Exception, e:
                Logger.Error('%s - AggregationController.AggregateMultipleDataPointHistoryWithAction - error:%s' % (__name__, e))
                Logger.Info('%s - AggregationController.AggregateMultipleDataPointHistoryWithAction - finished' % __name__)
                return
            content_from_solr = response['response']['docs']
            content_with_action_applied = apply_actions_to_content_with_historical_check(content_from_solr, [action])
            post_content_to_solr(content_with_action_applied)
        Logger.Info('%s - AggregationController.AggregateMultipleDataPointHistoryWithAction - finished' % __name__)

class DashboardAggregator(object):
    def __init__(self, dashboard):
        self.dashboard = dashboard

    def aggregate(self):
        for collection in self.dashboard.collections:
            for data_point in collection['data_points']:
                run_aggregator_for_data_point(data_point, collection['actions'])


class _UserThread(threading.Thread):
    def __init__(self, user):
        self.user = user
        threading.Thread.__init__(self)

    def run(self):
        finished = 0
        def producer(q, data_points_with_actions):
            for data_point_with_actions in data_points_with_actions:
                thread = _DataPointThread(data_point_with_actions)
                thread.start()
                q.put(thread, True)
        def consumer(q, data_points_count):
            while finished <= data_points_count:
                thread = q.get(True)
                thread.join()
                finished += 1
        Logger.Info('%s - AggregationController._UserThread.run - started' % __name__)
        Logger.Debug('%s - AggregationController._UserThread.run - started with user: %s' % (__name__, self.user))
        all_data_points_with_actions = []
        dc = DashboardsController(self.user)
        for dashboard in dc.get_live_dashboard():
            for collection in dashboard['collections']:
                actions = collection['actions']
                for data_point in collection['data_points']:
                    all_data_points_with_actions.append({'data_point':data_point, 'actions':actions})
        if all_data_points_with_actions:
            q = Queue(1)
            producer_thread = threading.Thread(target=producer, args=(q, all_data_points_with_actions))
            consumer_thread = threading.Thread(target=consumer, args=(q, len(all_data_points_with_actions)))
            producer_thread.start()
            consumer_thread.start()
        Logger.Info('%s - AggregationController._UserThread.run - finished' % __name__)

class _DataPointThread(threading.Thread):
    def __init__(self, data_point_with_actions):
        self.data_point_with_actions = data_point_with_actions
        threading.Thread.__init__(self)

    def run(self):
        Logger.Info('%s - AggregationController._DataPointThread.run - started' % __name__)
        Logger.Debug('%s - AggregationController._DataPointThread.run - started with data_point: %s' % (__name__, self.data_point_with_actions))
        run_aggregator_for_data_point(self.data_point_with_actions['data_point'], self.data_point_with_actions['actions'])
        Logger.Info('%s - AggregationController._DataPointThread.run - finished' % __name__)

def run_aggregator_for_data_point(data_point, actions=None):
    Logger.Info('%s - run_aggregator_for_data_point - started' % __name__)
    Logger.Debug('%s - run_aggregator_for_data_point - started with data_point:%s and actions:%s' % (__name__, data_point, actions))
    if not actions:
        actions = []
    dpc = DataPointController(data_point)
    content = dpc.run_data_point()
    content = _filter_content_by_last_successful_run(actions, content, data_point)
    apply_actions_and_post_to_solr(actions, content)
    Logger.Info('%s - run_aggregator_for_data_point - finished' % __name__)

def post_content_to_solr(content, commit=True):
    Logger.Info('%s - post_content_to_solr - started' % __name__)
    solr_url = settings.SOLR_CONFIG['solr_url']
    request_data = json.dumps(content)
    Logger.Debug('%s - post_content_to_solr - posting the following to solr: %s' % (__name__, request_data))
    try:
        solr_url = '%s/%s/%s' % (solr_url, settings.SOLR_CONFIG['solr_update_url'],  '?commit=true' if commit else '')
        request = urllib2.Request(solr_url, request_data, {'Content-Type': 'application/json'})
        response = urllib2.urlopen(request)
        response_stream = response.read()
        Logger.Debug('%s - post_content_to_solr - solr returned: %s' % (__name__, response_stream))
    except Exception, e:
        Logger.Error('%s - post_content_to_solr - error: %s' % (__name__, e))
    Logger.Info('%s - run_aggregator_for_data_point - finished' % __name__)

def apply_actions_to_content_with_historical_check(content, actions):
    Logger.Info('%s - apply_actions_to_content_with_historical_check - stated' % __name__)
    Logger.Debug('%s - apply_actions_to_content_with_historical_check - stated with content:%s and action:%s' % (__name__, content, actions))
    solr_url = settings.SOLR_CONFIG['solr_url']
    content_id_query_parts = ['id:%s' % item['id'] for item in content]
    solr_url = '%s/select/' % solr_url
    solr_data = 'q=*&wt=json&rows=%i&fq=%s' % (len(content_id_query_parts), '%20OR%20'.join(content_id_query_parts))
    try:
        request = urllib2.Request(solr_url, data=solr_data)
        response = urllib2.urlopen(request)
        response = json.loads(response.read())
    except Exception, e:
        Logger.Error('%s - apply_actions_to_content_with_historical_check - error:%s' % (__name__, e))
        Logger.Info('%s - apply_actions_to_content_with_historical_check - finished' % __name__)
        return content
    content_from_solr = response['response']['docs']
    content_ids_from_solr = [item['id'] for item in content_from_solr]
    content_ids_not_in_solr = [item['id'] for item in content if item['id'] not in content_ids_from_solr]
    content_not_in_solr = [item for item in content if item['id'] in content_ids_not_in_solr]
    return_content = content[:]
    for action in actions:
        ac = ActionController(action)
        content_id_in_solr_requiring_action = ac.extract_ids_of_content_without_action_applied(content_from_solr)
        content_in_solr_requiring_action = [item for item in content_from_solr if item['id'] in content_id_in_solr_requiring_action]
        content_requiring_action = content_not_in_solr + content_in_solr_requiring_action
        content_with_action_applied = ac.run_action(content_requiring_action)
        for item in content_with_action_applied:
            already_exists = False
            for return_item in return_content:
                if return_item['id'] == item['id']:
                    for key in item.keys():
                        return_item[key] = item[key]
                        already_exists = True
            if not already_exists:
                return_content.append(item)
    Logger.Info('%s - apply_actions_to_content_with_historical_check - finished' % __name__)
    return return_content

def apply_actions_to_content_without_historical_check(content, actions):
    Logger.Info('%s - apply_actions_to_content_without_historical_check - stated' % __name__)
    Logger.Debug('%s - apply_actions_to_content_without_historical_check - stated with content:%s and action:%s' % (__name__, content, actions))
    return_content = content[:]
    for action in actions:
        ac = ActionController(action)
        content_requiring_action = content
        content_with_action_applied = ac.run_action(content_requiring_action)
        for item in content_with_action_applied:
            already_exists = False
            for return_item in return_content:
                if return_item['id'] == item['id']:
                    for key in item.keys():
                        return_item[key] = item[key]
                        already_exists = True
            if not already_exists:
                return_content.append(item)
    Logger.Info('%s - apply_actions_to_content_without_historical_check - finished' % __name__)
    return return_content

def _filter_content_by_last_successful_run(actions, content, data_point):
    last_successful_run = RunRecord.LastSuccess(data_point, actions)
    if last_successful_run:
        content = [item for item in content if 'time' in item and item['time'] > last_successful_run]
    RunRecord.RecordRun(data_point, actions)
    return content

def _parse_content_item(content_item):
    def get_postfix(type):
        if type == 'string': return 's'
        if type == 'location_string': return 's'
        if type == 'location_point': return 's'
        if type == 'float': return 'f'
        return '_s'
    Logger.Info('%s - _parse_content_item - stated' % __name__)
    Logger.Debug('%s - _parse_content_item - stated with content_item:%s' % (__name__, content_item))
    return_data = {}
    for key in ['id', 'time', 'link']:
        if key in content_item and content_item[key]:
            return_data[key] = content_item[key]
    return_data.update(_map_text_from_content_item(content_item['text']))
    if 'author' in content_item:
        for key in ['display_name', 'link', 'image']:
            if key in content_item['author']:
                return_data['author_%s' % key] = content_item['author'][key]
    if 'channel' in content_item:
        for key in ['id', 'type', 'sub_type']:
            if key in content_item['channel']:
                return_data['channel_%s' % key] = content_item['channel'][key]
    if 'source' in content_item:
        for key in ['id', 'id_string', 'display_name']:
            if key in content_item['source']:
                return_data['source_%s' % key] = content_item['source'][key]
    if 'extensions' in content_item and isinstance(content_item['extensions'], dict):
        for key, value in content_item['extensions'].items():
            type = value['type'] if 'type' in value else 'string'
            return_data_key = 'extensions_%s_%s' % (key, get_postfix(type))
            return_data[return_data_key] = value['value'] if 'value' in value else value
    Logger.Info('%s - _parse_content_item - finished' % __name__)
    return return_data

def _map_text_from_content_item(text_array):
    Logger.Info('%s - _map_text_from_content_item - stated' % __name__)
    Logger.Debug('%s - _map_text_from_content_item - stated with text_array:%s' % (__name__, text_array))
    #TODO For now this does not support multi language
    if not len(text_array):
        return {}
    text = text_array[0]
    return_data = {}
    for key in ['language', 'title', 'text', 'tags']:
        if key in text and text[key]:
            return_data[key] = text[key]
    Logger.Info('%s - _map_text_from_content_item - finished' % __name__)
    return return_data

def apply_actions_and_post_to_solr(actions, content, check_for_existing_content=True):
    content = [_parse_content_item(item) for item in content]
    if actions and len(actions):
        if check_for_existing_content:
            content = apply_actions_to_content_with_historical_check(content, actions)
        else:
            content = apply_actions_to_content_without_historical_check(content, actions)
    post_content_to_solr(content, check_for_existing_content)

