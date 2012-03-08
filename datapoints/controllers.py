from django.conf import settings
from logger import Logger
from utils import my_import

class DataPointController(object):
    def __init__(self, data_point):
        Logger.Info('%s - DataPointController.__init__ - started' % __name__)
        Logger.Debug('%s - DataPointController.__init__ - started with data_point:%s' % (__name__, data_point))
        self.data_point = data_point
        Logger.Info('%s - DataPointController.__init__ - finished' % __name__)

    @classmethod
    def GetAllForTemplateOptions(cls, options):
        #TODO: need to take account of options
        Logger.Info('%s - DataPointController.GetAllForTemplateOptions - started' % __name__)
        Logger.Debug('%s - DataPointController.GetAllForTemplateOptions - started with options:%s' % (__name__, options))
        data_points = [DataPointController.LoadDataPoint(dp).get_unconfigured_config() for dp in settings.DATA_POINTS_CONFIG['enabled_data_points']]
        Logger.Info('%s - DataPointController.GetAllForTemplateOptions - finished' % __name__)
        return data_points

    def is_valid(self):
        Logger.Info('%s - DataPointController.is_valid - started' % __name__)
        type = self.data_point['type']
        data_point = DataPointController.LoadDataPoint(type)
        passed, errors = data_point.validate_config(self.data_point)
        Logger.Info('%s - DataPointController.is_valid - finished' % __name__)
        return passed, errors

    def get_configured_display_name(self):
        Logger.Info('%s - DataPointController.get_configured_display_name - started' % __name__)
        type = self.data_point['type']
        data_point = DataPointController.LoadDataPoint(type)
        display_name = data_point.generate_configured_display_name(self.data_point)
        Logger.Info('%s - DataPointController.get_configured_display_name - finished' % __name__)
        return display_name

    def data_point_added(self):
        Logger.Info('%s - DataPointController.data_point_added - started' % __name__)
        type = self.data_point['type']
        data_point = DataPointController.LoadDataPoint(type)
        data_point.data_point_added(self.data_point)
        Logger.Info('%s - DataPointController.data_point_added - finished' % __name__)

    def data_point_removed(self):
        Logger.Info('%s - DataPointController.data_point_removed - started' % __name__)
        type = self.data_point['type']
        data_point = DataPointController.LoadDataPoint(type)
        data_point.data_point_removed(self.data_point)
        Logger.Info('%s - DataPointController.data_point_removed - finished' % __name__)

    def generate_configured_guid(self):
        Logger.Info('%s - DataPointController.generate_configured_guid - started' % __name__)
        type = self.data_point['type']
        data_point = DataPointController.LoadDataPoint(type)
        guid = data_point.generate_configured_guid(self.data_point)
        Logger.Info('%s - DataPointController.generate_configured_guid - finished' % __name__)
        return guid

    def get_content_item_template(self):
        Logger.Info('%s - DataPointController.get_content_item_template - started' % __name__)
        type = self.data_point['type']
        data_point = DataPointController.LoadDataPoint(type)
        item_template = data_point.get_content_item_template()
        Logger.Info('%s - DataPointController.get_content_item_template - finished' % __name__)
        return item_template

    def run_data_point(self):
        Logger.Info('%s - DataPointController.run_data_point - started' % __name__)
        type = self.data_point['type']
        data_point = DataPointController.LoadDataPoint(type)
        content_items = data_point.tick(self.data_point)
        Logger.Info('%s - DataPointController.run_data_point - finished' % __name__)
        return content_items

    @classmethod
    def LoadDataPoint(cls, data_point_name):
        Logger.Info('%s - DataPointController.LoadDataPoint - started' % __name__)
        Logger.Debug('%s - DataPointController.LoadDataPoint - started with data_point_name:%s' % (__name__, data_point_name))
        data_point = my_import('metalayercore.datapoints.lib.%s.datapoint' % data_point_name)
        data_point = getattr(data_point, 'DataPoint')()
        Logger.Info('%s - DataPointController.LoadDataPoint - finished' % __name__)
        return data_point

    @classmethod
    def ExtractAPIKeyHelp(cls, data_point_name):
        Logger.Info('%s - DataPointController.ExtractAPIKeyHelp - started' % __name__)
        Logger.Debug('%s - DataPointController.ExtractAPIKeyHelp - started with data_point_name:%s' % (__name__, data_point_name))
        data_point = my_import('metalayercore.datapoints.lib.%s.datapoint' % data_point_name)
        data_point = getattr(data_point, 'DataPoint')()
        api_element = [e for e in data_point.get_unconfigured_config()['elements'] if e['name'] == 'api_key'][0]
        help_text = api_element['help']
        Logger.Info('%s - DataPointController.ExtractAPIKeyHelp - finished' % __name__)
        return help_text