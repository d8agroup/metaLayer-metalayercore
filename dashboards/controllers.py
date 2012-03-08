import time
from metalayercore.dashboards.models import Dashboard, DashboardTemplate
from logger import Logger
from math import ceil
from django.conf import settings
import constants

class DashboardsController(object):
    def __init__(self, user):
        Logger.Info('%s - DashboardsController - started' % __name__)
        Logger.Debug('%s - DashboardsController - started with user:%s' % (__name__, user))
        self.user = user
        Logger.Info('%s - DashboardsController - finished' % __name__)

    @classmethod
    def GetDashboardById(cls, id, increment_load_count=True):
        Logger.Info('%s - DashboardsController.GetDashboardById - started' % __name__)
        Logger.Debug('%s - DashboardsController.GetDashboardById - started with id:%s' % (__name__, id))
        dashboard = Dashboard.Load(id, increment_load_count)
        Logger.Info('%s - DashboardsController.GetDashboardById - finished' % __name__)
        return dashboard

    @classmethod
    def GetTendingDashboards(cls, count):
        Logger.Info('%s - DashboardsController.GetTendingDashboards - started' % __name__)
        Logger.Debug('%s - DashboardsController.GetTendingDashboards - started with count:%s' % (__name__, count))
        dashboards = Dashboard.Trending(count)
        Logger.Info('%s - DashboardsController.GetTendingDashboards - finished' % __name__)
        return dashboards

    @classmethod
    def GetTopDashboards(cls, count):
        Logger.Info('%s - DashboardsController.GetTopDashboards - started' % __name__)
        Logger.Debug('%s - DashboardsController.GetTopDashboards - started with count:%s' % (__name__, count))
        dashboards = Dashboard.Top(count)
        Logger.Info('%s - DashboardsController.GetTopDashboards - finished' % __name__)
        return dashboards

    @classmethod
    def GetRecentDashboards(cls, count):
        Logger.Info('%s - DashboardsController.GetRecentDashboards - started' % __name__)
        Logger.Debug('%s - DashboardsController.GetRecentDashboards - started with count:%s' % (__name__, count))
        dashboards = Dashboard.Recent(count)
        Logger.Info('%s - DashboardsController.GetRecentDashboards - finished' % __name__)
        return dashboards

    @classmethod
    def GetCategoryCount(cls, c):
        return len([d for d in Dashboard.objects.all() if 'categories' in d.config and c in d.config['categories']])

    @classmethod
    def GetDashboardsInCategory(cls, category, page=None, num_per_page=None):
        
        errors = []
        
        try:
            page = int(page) if page is not None else 1
        except ValueError:
            errors.append(constants.PAGE_NUMBER_INVALID)
        
        try:
            num_per_page = int(num_per_page) if num_per_page is not None else settings.MAX_INSIGHTS_PER_PAGE
        except ValueError:
            errors.append(constants.NUM_PER_PAGE_INVALID)
        
        if len(errors) > 0:
            return False, errors, None, None
        
        all_dashboards = Dashboard.collection.find({'config.categories':category})
        
        attributes = {}

        start = (page - 1) * num_per_page
        end = (page - 1) * num_per_page + num_per_page
        max_page = int(ceil(float(all_dashboards.count()) / float(num_per_page)))
        
        dashboards = all_dashboards[start:end]
        
        # since we can't iterate over or use the len() function on the dashboards collection, we 
        # use some math here to calculate the length of the collection.
        if start + num_per_page <= dashboards.count():
            dashboard_count = num_per_page
        else:
            dashboard_count = dashboards.count() - start
        
        attributes['count'] = dashboard_count
        attributes['next_page'] = page + 1 if max_page > page else None
        attributes['prev_page'] = page - 1 if page > 1 and dashboard_count > 0 else None
        attributes['num_per_page'] = num_per_page
        attributes['max_page'] = max_page
        attributes['page'] = page
        attributes['pages'] = _pagination(page, max_page)
        
        return True, [], dashboards, attributes

    @classmethod
    def RecordDashboardView(cls, dashboard_id):
        dashboard = DashboardsController.GetDashboardById(dashboard_id)
        dashboard.change_community_value('views', 1)

    @classmethod
    def GetRemixes(cls, insight_id, count):
        dashboards = [d for d in Dashboard.objects.all() if d.community['parent'] == insight_id]
        dashboards = sorted(dashboards, key=lambda x: x['last_saved'], reverse=True)
        return dashboards[:count]

    @classmethod
    def DeleteDashboardById(cls, dashboard_id):
        dashboard = DashboardsController.GetDashboardById(dashboard_id)
        dashboard.delete()

    def get_saved_dashboards(self, count=0):
        Logger.Info('%s - get_saved_dashboards - started' % __name__)
        saved_dashboards = Dashboard.AllForUser(self.user)
        if count:
            saved_dashboards = saved_dashboards[:count]
        Logger.Info('%s - get_saved_dashboards - finished' % __name__)
        return saved_dashboards

    def get_live_dashboard(self, count=0):
        Logger.Info('%s - get_live_dashboard - started' % __name__)
        saved_dashboards = Dashboard.AllForUser(self.user)
        saved_dashboards = [d for d in saved_dashboards if 'live' not in d['config'] or d['config']['live']]
        if count:
            saved_dashboards = saved_dashboards[:count]
        Logger.Info('%s - get_live_dashboard - finished' % __name__)
        return saved_dashboards

    def get_dashboard_by_id(self, id):
        Logger.Info('%s - get_dashboard_by_id - started' % __name__)
        Logger.Debug('%s - get_dashboard_by_id - started with id:%s' % (__name__, id))
        dashboard = DashboardsController.GetDashboardById(id)
        Logger.Info('%s - get_dashboard_by_id - finished' % __name__)
        return dashboard

    def delete_dashboard_by_id(self, id):
        Logger.Info('%s - delete_dashboard_by_id - started' % __name__)
        Logger.Debug('%s - delete_dashboard_by_id - started with id:%s' % (__name__, id))
        dashboard = Dashboard.Load(id)
        should_be_saved = False
        for c in dashboard['collections']:
            if 'data_points' in c and c['data_points']:
                should_be_saved = True
        if should_be_saved:
            dashboard.active = False
            dashboard.save()
        else:
            dashboard.remove()
        Logger.Info('%s - delete_dashboard_by_id - finished' % __name__)

    def get_dashboard_templates(self):
        Logger.Info('%s - get_dashboard_templates - started' % __name__)
        dashboard_templates = DashboardTemplate.AllForUser(self.user)
        Logger.Info('%s - get_dashboard_templates - finished' % __name__)
        return dashboard_templates

    def create_new_dashboard_from_template(self, template_id):
        Logger.Info('%s - create_new_dashboard_from_template - started' % __name__)
        Logger.Debug('%s - create_new_dashboard_from_template - started with template_id:%s' % (__name__, template_id))
        template = DashboardTemplate.GetTemplateById(template_id)
        dashboard = Dashboard.Create(self.user, template)
        Logger.Info('%s - get_dashboard_templates - finished' % __name__)
        return dashboard

    def create_new_dashboard_from_dashboard(self, dashboard_id):
        Logger.Info('%s - create_new_dashboard_from_dashboard - started' % __name__)
        Logger.Debug('%s - create_new_dashboard_from_dashboard - started with template_id:%s' % (__name__, dashboard_id))
        template = Dashboard.Load(dashboard_id)
        template.change_community_value('remixes', 1)
        dashboard = Dashboard.Create(self.user, template, True)
        Logger.Info('%s - create_new_dashboard_from_dashboard - finished' % __name__)
        return dashboard

    def create_new_dashboard_from_settings(self, settings):
        Logger.Info('%s - create_new_dashboard_from_settings - started' % __name__)
        Logger.Debug('%s - create_new_dashboard_from_settings - started with settings:%s' % (__name__, settings))
        dashboard = Dashboard.Create(self.user, settings)
        Logger.Info('%s - create_new_dashboard_from_settings - finished' % __name__)
        return dashboard

    def update_dashboard(self, dashboard):
        Logger.Info('%s - update_dashboard - started' % __name__)
        Logger.Debug('%s - update_dashboard - started with dashboard:%s' % (__name__, dashboard))
        db = Dashboard.Load(dashboard['id'])
        db.collections = dashboard['collections']
        db.name = dashboard['name']
        if 'config' in dashboard:
            db.config = dashboard['config']
        db.last_saved = time.time()
        db.save()
        Logger.Info('%s - update_dashboard - finished' % __name__)

    def delete_dashboards_to_match_subscription(self, maximum_number_of_dashboards):
        Logger.Info('%s - delete_dashboards_to_match_subscription - started' % __name__)
        Logger.Debug('%s - delete_dashboards_to_match_subscription - started with maximum_number_of_dashboards:%s' % (__name__, maximum_number_of_dashboards))
        dashboards_to_be_deleted = self.get_saved_dashboards()[maximum_number_of_dashboards:]
        for dashboard in dashboards_to_be_deleted:
            dashboard.active = False
            dashboard.save()
        Logger.Info('%s - delete_dashboards_to_match_subscription - finished' % __name__)

def _pagination(current_page, max_page):
    """
    Generates a list of pages to display for the purposes of pagination.
    
    """
    
    rounded_page = int(round(current_page, -1))
    
    if rounded_page < current_page:
        start_page = rounded_page + 1
        end_page = min(rounded_page + 10, max_page)
    else:
        start_page = rounded_page - 9
        end_page = min(rounded_page, max_page)
    
    return range(start_page, end_page + 1)
    
    
    

