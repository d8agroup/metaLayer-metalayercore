from hashlib import md5
import datetime
import time
from metalayercore.datapoints.classes import BaseDataPoint

class DataPoint(BaseDataPoint):
    def get_unconfigured_config(self):
        return {
            'type':'trssbox3twitterdata',
            'sub_type':'trssbox3twitterdata',
            'display_name_short':'Twitter',
            'full_display_name':'TRSS Provided Twitter Stream',
            'instructions':'Use this data point to search the TRSS provided tweet stream.',
            'image_large':'/static/images/thedashboard/data_points/twitter_large.png',
            'image_medium':'/static/images/thedashboard/data_points/twitter_medium.png',
            'image_small':'/static/images/thedashboard/data_points/twitter_small.png',
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
                    "<a href='${author_link}'>"\
                        "<img src='${author_image}' style='width:50px; padding:1px; box-shadow: 3px 3px 3px #111;' align='left' class='helper_corner tool_tip' title='<b>${author_display_name}</b> - click to view their profile on Twitter' />" \
                    "</a>"\
                    "<p style='float:left; padding:2px 0 0 8px;font-weight:bold;width:40%;overflow:hidden;height:12px;'>${author_display_name}</p>"\
                    "<p style='margin-bottom:2px;text-align:right'>"\
                    "<span style='position:relative;bottom:4px;right:10px;'>${pretty_date}</span>"\
                    "<img src='http://thomsonreuters.com/favicon.ico'/>"\
                    "</p>"\
                    "<a href='${link}'><p style='padding-left:60px;' class='tool_tip' title='click to see original post on Twitter+'>${title}</p></a>"\
                    "<ul style='padding-left:60px;' class='actions'></ul>"\
                "</li>"

    def generate_configured_guid(self, config):
        base_string = 'trssbox3twitterdata'
        return md5(base_string).hexdigest()

    def generate_configured_display_name(self, config):
        return config['full_display_name']

    def validate_config(self, config):
        return True, {}

    def tick(self, config):
        return []