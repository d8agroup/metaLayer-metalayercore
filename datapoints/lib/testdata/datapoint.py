import datetime
import time
from metalayercore.datapoints.classes import BaseDataPoint

class DataPoint(BaseDataPoint):
    def get_unconfigured_config(self):
        return {
            'type':'testdata',
            'sub_type':'testdata',
            'display_name_short':'Test Data',
            'full_display_name':'Test Data',
            'instructions':'Use this data point to search the public tweet stream.',
            'image_large':'http://metalayer.com/static/images/favicon.ico',
            'image_medium':'http://metalayer.com/static/images/favicon.ico',
            'image_small':'http://metalayer.com/static/images/favicon.ico',
            'configured':True,
            'elements':[
                self._generate_base_search_start_time_config_element(time.mktime(datetime.datetime(2012, 3, 14, 4, 0, 0).timetuple())),
                self._generate_base_search_end_time_config_element(time.mktime(datetime.datetime(2012, 3, 20, 23, 4, 0).timetuple()))
            ]
        }

    def get_content_item_template(self):
        return ""\
                "<li style='width:100%;'>"\
                    "<a href='${author_link}'>"\
                        "<img src='http://img.tweetimag.es/i/${author_display_name}_n' style='width:50px; padding:1px; box-shadow: 3px 3px 3px #111;' align='left' class='helper_corner tool_tip' title='<b>${author_display_name}</b> - click to view their profile on Twitter' />" \
                    "</a>"\
                    "<p style='float:left; padding:2px 0 0 8px;font-weight:bold;width:40%;overflow:hidden;height:12px;'>${author_display_name}</p>"\
                    "<p style='margin-bottom:2px;text-align:right'>"\
                    "<span style='position:relative;bottom:4px;right:10px;'>${pretty_date}</span>"\
                    "<img src='http://www.draftfcb.com/favicon.ico' style='width:15px;'/>"\
                    "</p>"\
                    "<a href='${link}'><p style='padding-left:60px;' class='tool_tip' title='click to see original post on Twitter+'>${title}</p></a>"\
                    "<ul style='padding-left:60px;' class='actions'></ul>"\
                "</li>"

    def generate_configured_guid(self, config):
        return '932ef63c661d734ba7f2d11b88b815c1'

    def generate_configured_display_name(self, config):
        return config['full_display_name']

    def validate_config(self, config):
        return True, {}

    def tick(self, config):
        return []