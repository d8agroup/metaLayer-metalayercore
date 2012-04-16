from hashlib import md5
import datetime
import time
from metalayercore.datapoints.classes import BaseDataPoint

class DataPoint(BaseDataPoint):
    def get_unconfigured_config(self):
        return {
            'type':'trssbox3newsdata',
            'sub_type':'trssbox3newsdata',
            'display_name_short':'TRSS News Data',
            'full_display_name':'TRSS News Data',
            'instructions':'Use this data point to work with the TRSS Box3 News Data.',
            'image_large':'http://thomsonreuters.com/favicon.ico',
            'image_medium':'http://thomsonreuters.com/favicon.ico',
            'image_small':'http://thomsonreuters.com/favicon.ico',
            'configured':True,
            'elements':[
                self._generate_base_search_start_time_config_element(time.mktime(datetime.datetime(2009, 1, 1, 0, 0, 0).timetuple())),
                #self._generate_base_search_start_time_config_element(),
                #self._generate_base_search_end_time_config_element(time.mktime(datetime.datetime(2012, 5, 20, 23, 4, 0).timetuple()))
                self._generate_base_search_end_time_config_element()
            ]
        }

    def get_content_item_template(self):
        return ""\
               "<li style='width:100%;'>"\
               "<img src='http://thomsonreuters.com/favicon.ico' style='width:20px; padding-right:10px;' align='left'/>"\
               "<p style='float:right;padding-right:10px;'>${display_time2(time)}</p>"\
               "<p style='padding-left:30px;'>${author_display_name}<span style='font-weight:bold'> ${title}</span></p>"\
               "<p style='padding-left:30px;padding-top:5px;'>${text}</p>"\
               "<ul style='padding-left:30px;' class='actions'></ul>"\
               "</li>"

    def generate_configured_guid(self, config):
        base_string = 'trssbox3newsdata'
        return md5(base_string).hexdigest()

    def generate_configured_display_name(self, config):
        return config['full_display_name']

    def validate_config(self, config):
        return True, {}

    def tick(self, config):
        return []