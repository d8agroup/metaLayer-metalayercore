from hashlib import md5
from urllib2 import urlopen
from urllib import quote
from metalayercore.datapoints.classes import BaseDataPoint
from logger import Logger
from django.utils import simplejson as json
from dateutil import parser as dateutil_parser, tz
import time
import datetime

class DataPoint(BaseDataPoint):
    def get_unconfigured_config(self):
        return {
            'type':'inqtelboard',
            'sub_type':'inqtelboard',
            'is_live':True,
            'display_name_short':'Message Boards',
            'full_display_name':'Message Boards Search',
            'instructions':'',
            'image_large':'/static/images/thedashboard/data_points/forum_large.png',
            'image_medium':'/static/images/thedashboard/data_points/forum_medium.png',
            'image_small':'/static/images/thedashboard/data_points/forum_small.png',
            'configured':True,
            'elements':[{
                'name':'keywords',
                'display_name':'What to search for',
                'help':'The keywords or hashtags that you want to use to search Message Boards',
                'type':'text',
                'value':''},
                self._generate_base_search_start_time_config_element(start_time=time.mktime(datetime.datetime(2013,2,17).timetuple())),
                self._generate_base_search_end_time_config_element()],
            'meta_data':[
                {
                    'display_name':'Channel',
                    'name':'source_display_name',
                    'type':'string'
                }
            ]
        }

    def get_content_item_template(self):
        return ""\
                "<li style='width:100%;'>"\
                    "<img src='/static/images/thedashboard/data_points/forum_medium.png' style='width:50px; padding:1px; box-shadow: 3px 3px 3px #111;' align='left' class='helper_corner'  />" \
                    "<p style='margin-bottom:2px;text-align:right'>"\
                    "<span style='position:relative;bottom:4px;right:10px;'>${pretty_date}</span>"\
                    "<img src='/static/images/thedashboard/data_points/forum_small.png' style='width:15px;'/>"\
                    "</p>"\
                    "<a href='${author_link}' target='_blank'><p style='padding-left:60px;' class='tool_tip' title='click to see original post on Facebook'>${display_text_abstract(strip_html(title))}<br/>${display_text_abstract(strip_html(text))}</p></a>"\
                    "<ul style='padding-left:60px;' class='actions'>" \
                    "</ul>"\
                "</li>"

    def generate_configured_guid(self, config):
        base_string = 'inqtelboard_source'
        return md5(base_string).hexdigest()

    def generate_configured_display_name(self, config):
	return 'Message Boards: North Korea'
        #keywords = [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']
        #return '%s: %s' % (config['display_name_short'], keywords)

    def validate_config(self, config):
	return True, {}
        #keywords = [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']
        #if not keywords or not keywords.strip():
        #    return False, { 'keywords':['You must search for something'] }
        #return True, {}

    def tick(self, config):
	return
        Logger.Info('%s - tick - started - with config: %s' % (__name__, config))
        keywords = [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']
        keywords = quote(keywords)
        url = 'http://search.twitter.com/search.json?q=%s&rpp=50&result_type=recent' % keywords
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
            },
            'extensions':{
                'twitterusername':{ 'type':'string', 'value':item['from_user'] },
                'channel':{'type':'string', 'value':'Twitter'}
            }
        }
