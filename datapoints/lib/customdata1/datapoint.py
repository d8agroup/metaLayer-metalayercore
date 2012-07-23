from metalayercore.datapoints.classes import BaseDataPoint

class DataPoint(BaseDataPoint):
    def get_unconfigured_config(self):
        return {
            'type':'customdata1',
            'sub_type':'customdata1',
            'display_name_short':'Upload Your Data',
            'full_display_name':'Upload Your Own Data in CSV Format',
            'instructions':'Use this data point to upload your own data in csv format.<br/><br/>This feature is currently '
                           'under heavy development and at present is limited to only accept csv files of less than 100mb '
                           'and that have column headers in the first row.',
            'image_large':'/static/images/thedashboard/data_points/upload_large.png',
            'image_medium':'/static/images/thedashboard/data_points/upload_medium.png',
            'image_small':'/static/images/thedashboard/data_points/upload_small.png',
            'configured':False,
            'elements':[
                {
                    'name':'channel_id',
                    'display_name':'channel_id',
                    'help':'',
                    'type':'hidden',
                    'value':''
                },
                {
                    'name':'file_upload',
                    'display_name':'Data File (csv format)',
                    'help':'Files are limited to 100mb, must be csv format and have headers in the first row',
                    'type':'file_upload'
                },
#                self._generate_base_search_start_time_config_element(),
#                self._generate_base_search_end_time_config_element()
            ],
            'meta_data':[]
        }

    def get_content_item_template(self):
        return "CONTENT ITEM TEMPLATES FOR USER UPLOADED CONTENT ARE PROVIDED BY THE DATAUPLOADER TYPE"

    def generate_configured_guid(self, config):
        return [e for e in config['elements'] if e['name'] == 'channel_id'][0]['value']

    def generate_configured_display_name(self, config):
        return config['full_display_name']

    def validate_config(self, config):
        return True, {}

    def tick(self, config):
        return []