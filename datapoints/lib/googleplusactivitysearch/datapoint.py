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
            'type':'googleplusactivitysearch',
            'sub_type':'googleplusactivitysearch',
            'display_name_short':'Google+',
            'full_display_name':'Google+ Search',
            'instructions':self.advanced_feature_markup + '<br/>Use this data point to search the public Google+ activity stream.',
            'image_large':'/static/images/thedashboard/data_points/googleplus_large.png',
            'image_medium':'/static/images/thedashboard/data_points/googleplus_medium.png',
            'image_small':'/static/images/thedashboard/data_points/googleplus_small.png',
            'configured':False,
            'elements':[
                {
                    'name':'keywords',
                    'display_name':'What to search for',
                    'help':'The keywords or hashtags that you want to use to search Google+',
                    'type':'text',
                    'value':''
                },
                {
                    'name':'api_key',
                    'display_name':'Your Google+ api key',
                    'help':'Searching Google+ requires and api key. to get one or change your\'s, click '
                           '<a href="https://code.google.com/apis/console#access" target="_blank">'
                           'here</a>.<br/><br/>'
                           '<span class="extra">It\'s quite easy to get an API Key, just choose to create '
                           'a new project from the drop down menu in the top left of the screen, make '
                           'sure you turn on Google+ API in the services section then click on API '
                           'Access on the left and copy the API Key (found about half way down the screen) '
                           'into the box above and your done!</span>',
                    'type':'api_key',
                    'value':''
                },
            ]
        }

    def get_content_item_template(self):
        return ""\
                "<li style='width:100%;'>"\
                    "<a href='${author_link}'>" \
                        "<img src='${author_image}' style='width:50px; padding:1px; box-shadow: 3px 3px 3px #111;' align='left' class='helper_corner tool_tip' title='<b>${author_display_name}</b> - click to view their profile in Google+' />" \
                    "</a>" \
                    "<p style='float:left; padding:2px 0 0 8px;font-weight:bold;width:40%;overflow:hidden;height:12px;'>${author_display_name}</p>"\
                    "<p style='margin-bottom:2px;text-align:right'>"\
                        "<span style='position:relative;bottom:4px;right:10px;'>${pretty_date}</span>"\
                        "<img src='/static/images/lib/yoo/google_plus_2424.png' style='width:15px;'/>"\
                    "</p>"\
                    "<a href='${link}'><p style='padding-left:60px;' class='tool_tip' title='click to see original post in Google+'>${title}</p></a>"\
                "</li>"

    def generate_configured_guid(self, config):
        base_string = ' '.join([e['value'] for e in config['elements']])
        return md5(base_string).hexdigest()

    def generate_configured_display_name(self, config):
        keywords = [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']
        return '%s: %s' % (config['display_name_short'], keywords)

    def validate_config(self, config):
        keywords = [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']
        api_key = [e for e in config['elements'] if e['name'] == 'api_key'][0]['value']

        errors = { 'keywords':[], 'api_key':[] }
        if not keywords or not keywords.strip():
            errors['keywords'].append('You must search for something.')

        if not api_key or not api_key.strip():
            errors['api_key'].append('You must provide an api key')

        #TODO should validate the api key here

        if errors['keywords'] or errors['api_key']:
            return False, errors
        return True, {}

    def tick(self, config):
        Logger.Info('%s - tick - started - with config: %s' % (__name__, config))
        api_key = [e for e in config['elements'] if e['name'] == 'api_key'][0]['value']
        keywords = [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']
        keywords = quote(keywords)
        url = 'https://www.googleapis.com/plus/v1/activities?query=%s&pp=1&key=%s' % (keywords, api_key)
        response = urlopen(url).read()
        Logger.Debug('%s - tick - raw response: %s' % (__name__, response))
        response = json.loads(response)
        Logger.Debug('%s - tick - JSON response: %s' % (__name__, response))
        content = [self._map_googleplus_item_to_content_item(config, item) for item in response['items']]
        Logger.Info('%s - tick - finished' % __name__)
        return content

    def _map_googleplus_item_to_content_item(self, config, item):
        return {
            'id':item['id'],
            'text':[ { 'title':item['title'], } ],
            'time': time.mktime(dateutil_parser.parse(item['updated']).astimezone(tz.tzutc()).timetuple()),
            'link':item['url'],
            'author':{
                'display_name':item['actor']['displayName'],
                'link':item['actor']['url'],
                'image':item['actor']['image']['url']
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