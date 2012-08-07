from django.conf import settings
from logger import Logger
from utils import my_import

class DataPointController(object):
    """
    DataPointController acts as the main entry point to the DataPoints package.
    """
    def __init__(self, data_point):
        """
        DataPointController instance constructor

        Arguments
        ---------
        data_point (dict): the configuration dictionary taken from the result of calling::
            data_point_instance.get_unconfigured_config()

        Returns
        -------
        Instance of DataPointController
        """
        Logger.Info('%s - DataPointController.__init__ - started' % __name__)
        Logger.Debug('%s - DataPointController.__init__ - started with data_point:%s' % (__name__, data_point))
        self.data_point = data_point
        Logger.Info('%s - DataPointController.__init__ - finished' % __name__)

    @classmethod
    def GetAllForTemplateOptions(cls, options):
        """
        Class Method: Return the configuration for all DataPoints to be rendered in a dashboard

        Notes
        -----
        This method currently relies on the presence of the following setting::
            settings.DATA_POINTS_CONFIG['enabled_data_points']]

        This setting should be a list of *names* of all DataPoints to to be included in new dashboards

        Arguments
        ---------
        options: Not currently supported

        Returns
        -------
        List of dict config for all matching DataPoint instances

        Raises
        ------
        AttributeError: if any of the configured datapoints can not be loaded
        """
        #TODO: need to take account of options
        Logger.Info('%s - DataPointController.GetAllForTemplateOptions - started' % __name__)
        Logger.Debug('%s - DataPointController.GetAllForTemplateOptions - started with options:%s' % (__name__, options))
        data_points = [DataPointController.LoadDataPoint(dp).get_unconfigured_config() for dp in settings.DATA_POINTS_CONFIG['enabled_data_points']]
        Logger.Info('%s - DataPointController.GetAllForTemplateOptions - finished' % __name__)
        return data_points

    def is_valid(self):
        """
        Calls the validate_config method on the DataPoint of which this DataPointController is the subject

        Returns
        -------
        Boolean, True if the configuration this DataPointController was constructed with is deemed to be valid by the
        DataPoint.

        Raises
        ------
        AttributeError: if the name of the data point that is the subject of this controller can not be loaded
        """
        Logger.Info('%s - DataPointController.is_valid - started' % __name__)
        type = self.data_point['type']
        data_point = DataPointController.LoadDataPoint(type)
        passed, errors = data_point.validate_config(self.data_point)
        Logger.Info('%s - DataPointController.is_valid - finished' % __name__)
        return passed, errors

    def oauth_credentials_are_valid(self, credentials_json):
        type = self.data_point['type']
        data_point = DataPointController.LoadDataPoint(type)
        return data_point.oauth_credentials_are_valid(credentials_json)

    def oauth_poll_for_new_credentials(self):
        type = self.data_point['type']
        data_point = DataPointController.LoadDataPoint(type)
        return data_point.oauth_poll_for_new_credentials(self.data_point)

    def get_oauth_authenticate_url(self):
        type = self.data_point['type']
        data_point = DataPointController.LoadDataPoint(type)
        return data_point.oauth_get_oauth_authenticate_url(self.data_point['id'])

    def update_data_point_with_oauth_dependant_config(self):
        """
        Return a configured data point based on the recently successful oauth authorisation

        Returns
        -------
        Dict: a copy of the data point that is the subject of this controller enhanced with any oauth dependant config
        """
        type = self.data_point['type']
        data_point = DataPointController.LoadDataPoint(type)
        enhanced_data_point = data_point.update_data_point_with_oauth_dependant_config(self.data_point)
        return enhanced_data_point

    def get_configured_display_name(self):
        """
        Return the fully configured display name for the data point that this controller is the subject of

        Returns
        -------
        String: the fully configured display name of the data point that is the subject of this controller

        Raises
        ------
        AttributeError: if the name of the data point that is the subject of this controller can not be loaded
        """
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

    def get_metadata_filters(self):
        if self.data_point and 'meta_data' in self.data_point:
            return self.data_point['meta_data']
        data_point = DataPointController.LoadDataPoint(self.data_point['type'])
        config = data_point.get_unconfigured_config()
        available_filters = config['meta_data'] if 'meta_data' in config else []
        return available_filters

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

    @classmethod
    def DecodeSearchPropertyDisplayName(cls, search_encoded_name):
        if not search_encoded_name.startswith('extensions_'):
            return search_encoded_name
        search_encoded_name_parts = search_encoded_name.split('_')
        if len(search_encoded_name_parts) <> 3:
            return search_encoded_name
        return search_encoded_name_parts[1]
