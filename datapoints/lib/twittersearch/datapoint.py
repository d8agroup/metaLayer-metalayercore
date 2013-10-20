from hashlib import md5
from urllib2 import urlopen
from urllib import quote
from metalayercore.datapoints.classes import BaseDataPoint
from logger import Logger
from django.utils import simplejson as json
from dateutil import parser as dateutil_parser, tz
import time
import datetime
from twython import Twython
from django.conf import settings

class DataPoint(BaseDataPoint):
    def get_unconfigured_config(self):
        return {
            'type':'twittersearch',
            'sub_type':'twittersearch',
            'is_live':True,
            'display_name_short':'Twitter',
            'full_display_name':'Twitter Search',
            'instructions':'Use this data point to search the public tweet stream. Twitter entities such as #hashtags, @replies, and $CASHTAGS are available.',
            'image_large':'/static/images/thedashboard/data_points/twitter_large.png',
            'image_medium':'/static/images/thedashboard/data_points/twitter_medium.png',
            'image_small':'/static/images/thedashboard/data_points/twitter_small.png',
            'configured':False,
            'elements':[{
                'name':'keywords',
                'display_name':'What to search for',
                'help':'The keywords or hashtags that you want to use to search Twitter',
                'type':'text',
                'value':''},
                self._generate_base_search_start_time_config_element(start_time=time.mktime((datetime.datetime.utcnow() - datetime.timedelta(hours=1)).timetuple())),
                self._generate_base_search_end_time_config_element()],
            'meta_data':[
                {
                    'display_name':'Twitter Username',
                    'name':'extensions_twitterusername_s',
                    'type':'string'
                },
                {
                    'display_name':'Channel',
                    'name':'extensions_channel_s',
                    'type':'string'
                }
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
                    "<img src='/static/images/thedashboard/data_points/twitter_small.png' style='width:15px;'/>"\
                    "</p>"\
                    "<a href='${link}'><p style='padding-left:60px;' class='tool_tip' title='click to see original post on Twitter+'>${title}</p></a>"\
                    "<ul style='padding-left:60px;' class='actions'>" \
                    "    <li class='action_values' style='margin-top:5px;'>" \
                    "       <label>Twitter Username</label>" \
                    "       <span style='font-weight:bold;'>" \
                    "           <a class='action_inline_filter' data-facet_name='extensions_twitterusername_s' data-facet_value='${extensions_twitterusername_s}'>${extensions_twitterusername_s}</a>"\
                    "       </span>" \
                    "   </li>" \
                    "</ul>"\
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
        # keywords = quote(keywords)
        # url = 'http://search.twitter.com/search.json?q=%s&rpp=50&result_type=recent' % keywords
        # response = urlopen(url).read()
        # Logger.Debug('%s - tick - raw response: %s' % (__name__, response))
        # response = json.loads(response)
        # Logger.Debug('%s - tick - JSON response: %s' % (__name__, response))
        twitter_api = Twython(
            settings.twython_config['app_key'],
            settings.twython_config['app_secret'],
            settings.twython_config['oauth_token'],
            settings.twython_config['oauth_secret'])
        raw_results = twitter_api.search(q=keywords, lang='en', results_type='recent', count=100)
        content = [self._map_twitter_item_to_content_item(config, item) for item in raw_results['statuses']]
        Logger.Info('%s - tick - finished' % __name__)
        return content

    def _map_twitter_item_to_content_item(self, config, raw_tweet):
        user = raw_tweet.get('user', {})
        screen_name = user.get('screen_name', None)
        return {
            'id':md5(raw_tweet['id_str']).hexdigest(),
            'text':[ { 'title':raw_tweet['text'].encode('ascii', 'ignore'), } ],
            'time': int(time.mktime(dateutil_parser.parse(raw_tweet['created_at']).astimezone(tz.tzutc()).timetuple())),
            'link':'https://twitter.com/#!/%s/status/%s' % (screen_name, raw_tweet['id_str']),
            'author':{
                'display_name': screen_name,
                'link':'https://twitter.com/#!/%s' % screen_name,
                'image':user.get('profile_image_url', None)
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
                'twitterusername':{ 'type':'string', 'value': screen_name},
                'channel':{'type':'string', 'value':'Twitter'}
            }
        }
