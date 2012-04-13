from hashlib import md5
import datetime
import time
from metalayercore.datapoints.classes import BaseDataPoint

class DataPoint(BaseDataPoint):
    def get_unconfigured_config(self):
        return {
            'type':'trssbox3facebookdata',
            'sub_type':'trssbox3facebookdata',
            'display_name_short':'Facebook',
            'full_display_name':'TRSS Provided Facebook Posts',
            'instructions':'Use this data point to search the TRSS provided facebook posts.',
            'image_large':'/static/images/thedashboard/data_points/facebook_medium.png',
            'image_medium':'/static/images/thedashboard/data_points/facebook_small.png',
            'image_small':'/static/images/thedashboard/data_points/facebook_small.png',
            'configured':True,
            'elements':[
                self._generate_base_search_start_time_config_element(time.mktime(datetime.datetime(2012, 4, 12, 0, 0, 0).timetuple())),
                #self._generate_base_search_start_time_config_element(),
                #self._generate_base_search_end_time_config_element(time.mktime(datetime.datetime(2012, 3, 20, 23, 4, 0).timetuple()))
                self._generate_base_search_end_time_config_element()
            ]
        }

    def get_content_item_template(self):
        return ""\
               "<li style='width:100%;'>"\
               "<img src='/static/images/thedashboard/data_points/facebook_small.png' style='width:20px; padding-right:10px;' align='left'/>"\
               "<p style='float:right;padding-right:10px;'>${pretty_date}</p>"\
               "<p style='padding-left:30px;'>${author_display_name}<span style='font-weight:bold'> ${title}</span></p>"\
               "<ul style='padding-left:30px;' class='actions'></ul>"\
               "</li>"

    def generate_configured_guid(self, config):
        base_string = 'trssbox3facebookdata'
        return md5(base_string).hexdigest()

    def generate_configured_display_name(self, config):
        return config['full_display_name']

    def validate_config(self, config):
        return True, {}

    def tick(self, config):
        return []