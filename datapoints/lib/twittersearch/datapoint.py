from hashlib import md5
from urllib2 import urlopen
from urllib import quote
from metalayercore.datapoints.classes import BaseDataPoint
from logger import Logger
from django.utils import simplejson as json
from dateutil import parser as dateutil_parser, tz
import time

class DataPoint(BaseDataPoint):
    def get_unconfigured_config(self):
        return {
            'type':'twittersearch',
            'sub_type':'twittersearch',
            'display_name_short':'Twitter',
            'full_display_name':'Twitter Search',
            'instructions':'Use this data point to search the public tweet stream.',
            'image_large':'/static/images/thedashboard/data_points/twitter_large.png',
            'image_medium':'/static/images/thedashboard/data_points/twitter_medium.png',
            'image_small':'/static/images/thedashboard/data_points/twitter_small.png',
            'configured':False,
            'elements':[
                {
                    'name':'keywords',
                    'display_name':'What to search for',
                    'help':'The keywords or hashtags that you want to use to search Twitter',
                    'type':'text',
                    'value':''
                },
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
                    "<img src='/static/images/lib/yoo/twitter_2424.png' style='width:15px;'/>"\
                    "</p>"\
                    "<a href='${link}'><p style='padding-left:60px;' class='tool_tip' title='click to see original post on Twitter+'>${title}</p></a>"\
                "</li>"

    def generate_configured_guid(self, config):
        base_string = 'twitter_search %s' % [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']
        return md5(base_string).hexdigest()

    def generate_configured_display_name(self, config):
        keywords = [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']
        return '%s: %s' % (config['display_name_short'], keywords)

    def validate_config(self, config):
        keywords = [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']
        if not keywords or not keywords.strip():
            return False, { 'keywords':['You must search for something'] }
        return True, {}

    def tick(self, config):
        Logger.Info('%s - tick - started - with config: %s' % (__name__, config))
        keywords = [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']
        keywords = quote(keywords)
        url = 'http://search.twitter.com/search.json?q=%s&rpp=50' % keywords
        response = urlopen(url).read()
        Logger.Debug('%s - tick - raw response: %s' % (__name__, response))
        response = json.loads(response)
        Logger.Debug('%s - tick - JSON response: %s' % (__name__, response))
        content = [self._map_twitter_item_to_content_item(config, item) for item in response['results']]
        Logger.Info('%s - tick - finished' % __name__)
        return content

    def _map_twitter_item_to_content_item(self, config, item):
        return {
            'id':md5(item['id_str']).hexdigest(),
            'text':[ { 'title':item['text'].encode('ascii', 'ignore'), } ],
            'time': int(time.mktime(dateutil_parser.parse(item['created_at']).astimezone(tz.tzutc()).timetuple())),
            'link':'https://twitter.com/#!/%s/status/%s' % (item['from_user'], item['id_str']),
            'author':{
                'display_name':item['from_user'],
                'link':'https://twitter.com/#!/%s' % item['from_user'],
                'image':item['profile_image_url']
            },
            'channel':{
                'id':md5(config['type'] + config['sub_type']).hexdigest(),
                'type':config['type'],
                'sub_type':config['sub_type']
            },
            'source':{
                'id':self.generate_configured_guid(config),
                'display_name':self.generate_configured_display_name(config),
            }
        }