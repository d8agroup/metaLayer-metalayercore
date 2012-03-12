import random
import string
from bson.objectid import ObjectId
from django.conf import settings
from django.core.cache import cache
from django.db import models
import time
from djangotoolbox.fields import DictField, ListField
from logger import Logger
from utils import get_pretty_date

class Dashboard(models.Model):
    class Meta:
        db_table = 'dashboards_dashboards'

    username = models.TextField()
    created = models.FloatField()
    accessed = models.IntegerField()
    last_saved_pretty = models.TextField()
    last_saved = models.FloatField()
    collections = ListField()
    widgets = DictField()
    active = models.BooleanField()
    deleted = models.BooleanField()
    name = models.TextField()
    config = DictField()
    community = DictField()
    id_string = models.TextField()
    short_url = DictField()

    @classmethod
    def Create(cls, user, template=None, template_is_dashboard=False):
        Logger.Info('%s - Dashboard.Create - started' % __name__)
        Logger.Debug('%s - Dashboard.Create - started with user:%s and template:%s' % (__name__, user, template))
        dashboard = Dashboard(
            username= user.username,
            created= time.time(),
            accessed=1,
            last_saved_pretty='Not yet used',
            last_saved=time.time(),
            collections=template['collections'] if template else {},
            widgets=template['widgets'] if template else {},
            active=False,
            deleted=False,
            name=template['name'],
            config={}
        )
        dashboard._ensure_community_defaults()
        for collection in dashboard.collections:
            collection['id'] = '%s' % ObjectId()
        if template_is_dashboard:
            dashboard.community['parent'] = template['id']
        dashboard.save()
        dashboard.id_string = '%s' % dashboard.id
        dashboard_short_url = DashboardShortUrl.Create(dashboard.id_string)
        dashboard.short_url = { 'url_identifier':dashboard_short_url.url_identifier, 'dashboard_id':dashboard_short_url.dashboard_id }
        dashboard.save()
        Logger.Info('%s - Dashboard.Create - finished' % __name__)
        return dashboard

    @classmethod
    def AllForUser(cls, user):
        Logger.Info('%s - Dashboard.AllForUser - started' % __name__)
        Logger.Debug('%s - Dashboard.AllForUser - started with user:%s' % (__name__, user))
        dashboards = Dashboard.objects.filter(username=user.username)
        dashboards = [d for d in dashboards if d.active == True and d.deleted == False]
        dashboards = sorted(dashboards, key=lambda dashboard: dashboard.last_saved, reverse=True)
        for dashboard in dashboards:
            dashboard.last_saved_pretty = dashboard._pretty_date(dashboard.last_saved)
        Logger.Info('%s - Dashboard.AllForUser - finished' % __name__)
        return dashboards

    @classmethod
    def Load(cls, id, increment_load_count = False):
        Logger.Info('%s - Dashboard.Load - started' % __name__)
        Logger.Debug('%s - Dashboard.Load - started with is:%s and increment_load_count:%s' % (__name__, id, increment_load_count))
        try:
            object_id = ObjectId(id)
        except Exception, e:
            Logger.Error('%s - Load - error: invalid object id supplied: %s' % (__name__, id))
            Logger.Info('%s - Dashboard.Load - finished' % __name__)
            return None
        try:
            dashboard = Dashboard.objects.get(id=object_id)
            dashboard.last_saved_pretty = dashboard._pretty_date(dashboard.last_saved)
            dashboard.created_pretty = dashboard._pretty_date(dashboard.created)
            if dashboard and increment_load_count:
                dashboard.accessed += 1
                dashboard.save()
        except Dashboard.DoesNotExist:
            Logger.Warn('%s - Dashboard.Load - error: could not load dashboard' % __name__)
            Logger.Debug('%s - Dashboard.Load - error: could not load dashboard with id:%s' % (__name__, id))
            dashboard = None
        Logger.Info('%s - Dashboard.Load - finished' % __name__)
        return dashboard

    @classmethod
    def Trending(cls, count):
        Logger.Info('%s - Dashboard.Trending - started' % __name__)
        Logger.Debug('%s - Dashboard.Trending - started with count:%s' % (__name__, count))
        cache_key = 'dashboards_models_dashboard_trending'
        cached_values = cache.get('%s_%i' % (cache_key, count), -1)
        if cached_values == -1:
            dashboards = [d for d in Dashboard.objects.filter(active=True, deleted=False)]
            random.shuffle(dashboards)
            cached_values = dashboards[:int(count)]
            cache.add('%s_%i' % (cache_key, count), cached_values, settings.LOW_LEVEL_CACHE_LIMITS[cache_key])
        Logger.Info('%s - Dashboard.Trending - finished' % __name__)
        return cached_values

    @classmethod
    def Top(cls, count):
        Logger.Info('%s - Dashboard.Top - started' % __name__)
        Logger.Debug('%s - Dashboard.Top - started with count:%s' % (__name__, count))
        cache_key = 'dashboards_models_dashboard_top'
        cached_values = cache.get(cache_key, -1)
        if cached_values == -1:
            dashboards = [d for d in Dashboard.objects.filter(active=True, deleted=False)]
            #random.shuffle(dashboards)
            sorted(dashboards, key=lambda d: d.community['views'] if 'views' in d.community else 0, reverse=True)
            cached_values = dashboards[:int(count)]
            cache.add(cache_key, cached_values, settings.LOW_LEVEL_CACHE_LIMITS[cache_key])
        Logger.Info('%s - Dashboard.Top - finished' % __name__)
        return cached_values

    @classmethod
    def Recent(cls, count):
        Logger.Info('%s - Dashboard.Recent - started' % __name__)
        Logger.Debug('%s - Dashboard.Recent - started with count:%s' % (__name__, count))
        cache_key = 'dashboards_models_dashboard_recent'
        cached_values = cache.get(cache_key, -1)
        if cached_values == -1:
            dashboards = [d for d in Dashboard.objects.filter(active=True, deleted=False)]
            dashboards = sorted(dashboards, key=lambda dashboard: dashboard.last_saved, reverse=True)
            dashboards = dashboards[:int(count)]
            for dashboard in dashboards:
                dashboard.last_saved_pretty = dashboard._pretty_date(dashboard.last_saved)
            cached_values = dashboards
            cache.add(cache_key, cached_values, settings.LOW_LEVEL_CACHE_LIMITS[cache_key])
        Logger.Info('%s - Dashboard.Recent - finished' % __name__)
        return cached_values

    def __getitem__(self, item):
        return getattr(self, item)

    def delete(self, using=None):
        self.deleted = True
        self.active = False
        self.config['live'] = False
        self.save()

    def save(self, *args, **kwargs):
        self.active = True if sum([len(c['data_points']) for c in self.collections if 'data_points' in c]) else False
        return super(Dashboard, self).save(*args, **kwargs)

    def change_community_value(self, value_type, value_change):
        self.community[value_type] += value_change
        self.save()

    def has_visualizations(self):
        for collection in [c for c in self.collections if c['data_points']]:
            if collection['visualizations']:
                for visualization in collection['visualizations']:
                    if 'snapshot' in visualization and visualization['snapshot']:
                        return True
        return False


    def visualization_for_image(self):
        for visualization_type in settings.VISUALIZATIONS_CONFIG['visualization_display_hierarchy']:
            for collection in [c for c in self.collections if c['data_points']]:
                for visualization in collection['visualizations']:
                    if visualization['name'] == visualization_type and 'snapshot' in visualization and visualization['snapshot']:
                        return visualization['snapshot']
        return None

    def visualization_by_id(self, visualization_id):
        for collection in [c for c in self.collections if c['data_points']]:
            for visualization in collection['visualizations']:
                if visualization['id'] == visualization_id and 'snapshot' in visualization and visualization['snapshot']:
                    return visualization['snapshot']
        return None

    def single_data_point_for_image(self):
        for collection in self.collections:
            for data_point in collection['data_points']:
                return data_point['image_medium']
        return 'http://%s/80/80/no_image.png' % settings.SITE_HOST

    def four_data_points_for_image(self):
        data_points = []
        for collection in self.collections:
            for data_point in collection['data_points']:
                data_points.append(data_point['image_medium'])
        return data_points[:4]

    def tz(self):
        start_times = [c['search_filters']['time'].split('%20TO%20')[0].strip('[') for c in self.collections if 'time' in c['search_filters']]
        end_times = [c['search_filters']['time'].split('%20TO%20')[1].strip(']') for c in self.collections if 'time' in c['search_filters']]
        start_times = [int(t) for t in start_times] if '*' not in start_times else []
        start_time = self._pretty_date(min(start_times)) if start_times else 'Historic'
        end_times = [int(t) for t in end_times] if '*' not in end_times else []
        end_time = self._pretty_date(max(end_times)) if end_times else 'Now'
        if start_time == end_time:
            return start_time
        return '%s to %s' % (start_time, end_time)

    def _pretty_date(self, time=False):
        return get_pretty_date(time)

    def _ensure_community_defaults(self):
        if not self.community:
            self.community = {
                'views':0,
                'remixes':0,
                'challenges':0,
                'comments':0
            }

class DashboardTemplate(object):
    @classmethod
    def AllForUser(cls, user):
        Logger.Info('%s - DashboardTemplate.AllForUser - started' % __name__)
        Logger.Debug('%s - DashboardTemplate.AllForUser - started with user:%s' % (__name__, user))
        #TODO this is a mock up
        Logger.Info('%s - DashboardTemplate.AllForUser - finished' % __name__)
        return [
            {
                'id':'g8f7h76j6hj5h45k46hjkhj87',
                'display_name':'Empty Dashboard',
                'description':'A blank dashboard ready for anything!',
                'image':'dashboard_template_images/empty_dashboard.gif',
                'collections':[{}, {}],
                'widgets':{'something':{}},
                'name':'Untitled Insight'
            }
        ]

    @classmethod
    def GetTemplateById(cls, id):
        Logger.Info('%s - DashboardTemplate.GetTemplateById - started' % __name__)
        Logger.Debug('%s - DashboardTemplate.GetTemplateById - started with id:%s' % (__name__, id))
        #TODO this is a mock up
        Logger.Info('%s - DashboardTemplate.GetTemplateById - finished' % __name__)
        return DashboardTemplate.AllForUser(None)[0]

class DashboardShortUrl(models.Model):
    url_identifier = models.TextField()
    dashboard_id = models.TextField()

    @classmethod
    def Create(cls, dashboard_id):
        def generate_random_string():
            return "".join( [random.choice(string.letters[:26]) for i in xrange(5)] )
        Logger.Info('%s - ShortUrl.Create - started' % __name__)
        Logger.Debug('%s - ShortUrl.Create - started with dashboard_id:%s ' % (__name__, dashboard_id))
        url_identifier = generate_random_string()
        while DashboardShortUrl.objects.filter(url_identifier=url_identifier).count():
            url_identifier = generate_random_string()
        short_url = DashboardShortUrl(
            url_identifier=url_identifier,
            dashboard_id=dashboard_id
        )
        short_url.save()
        Logger.Info('%s - ShortUrl.Create - finished' % __name__)
        return short_url

    @classmethod
    def Load(cls, url_identifier):
        Logger.Info('%s - ShortUrl.Load - started' % __name__)
        Logger.Debug('%s - ShortUrl.Load - started with url_identifier:%s' % (__name__, url_identifier))
        try:
            short_url = DashboardShortUrl.objects.get(url_identifier=url_identifier)
        except DashboardShortUrl.DoesNotExist:
            Logger.Warn('%s - DashboardShortcutUrl.Load - accessed with url_identifier that does not exists' % __name__)
            Logger.Debug('%s - DashboardShortcutUrl.Load - accessed with url_identifier that does not exists: %s' % (__name__, url_identifier))
            short_url = None
        Logger.Info('%s - ShortUrl.Load - finished' % __name__)
        return short_url

    @classmethod
    def Delete(cls, dashboard_id):
        Logger.Info('%s - ShortUrl.Delete - started' % __name__)
        Logger.Info('%s - ShortUrl.Delete - started with dashboard_id:%s' % (__name__, dashboard_id))
        short_url = DashboardShortUrl.objects.get(dashboard_id=dashboard_id)
        if short_url:
            short_url.delete()
        Logger.Info('%s - ShortUrl.Delete - finished' % __name__)