import time
import datetime
from hashlib import md5
from dateutil import parser as dateutil_parser, tz

import httplib2
from apiclient.discovery import build

from logger import Logger
from oauth2client.client import OAuth2WebServerFlow, Credentials
from metalayercore.datapoints.classes import BaseDataPoint
from metalayercore.oauth2bridge.controllers import GoogleOauth2Controller


class DataPoint(BaseDataPoint):
    flow = OAuth2WebServerFlow(
        client_id="THIS IS MANAGED ELSEWHERE",
        client_secret="THIS IS MANAGED ELSEWHERE",
        scope='https://www.googleapis.com/auth/plus.me',
        redirect_uri='THIS IS MANAGED ELSEWHERE')

    def get_unconfigured_config(self):
        return {
            'type':'googleplusactivitysearch',
            'sub_type':'googleplusactivitysearch',
            'is_live':True,
            'display_name_short':'Google+',
            'full_display_name':'Google+ Search',
            'instructions': '<br/>Use this data point to search the public Google+ activity stream.',
            'image_large':'/static/images/thedashboard/data_points/googleplus_large.png',
            'image_medium':'/static/images/thedashboard/data_points/googleplus_medium.png',
            'image_small':'/static/images/thedashboard/data_points/googleplus_small.png',
            'configured':False,
            'elements':[
                {
                    'name':'oauth2',
                    'display_name':'oauth2',
                    'help':"""To access data from Google+, you need to authorize Delv to collect data on your
                              behalf.<br/><br/>
                              Please click the Authorize button below, you will then be take to a Google web page so you can
                              authorize Delv.""",
                    'type':'oauth2',
                    'value':''
                },
                {
                    'name':'keywords',
                    'display_name':'What to search for',
                    'help':'The keywords or hashtags that you want to use to search Google+',
                    'type':'text',
                    'value':''
                },
                self._generate_base_search_start_time_config_element(start_time=time.mktime((datetime.datetime.utcnow() - datetime.timedelta(hours=2)).timetuple())),
                self._generate_base_search_end_time_config_element()
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
                        "<img src='/static/images/thedashboard/data_points/googleplus_small.png' style='width:15px;'/>"\
                    "</p>"\
                    "<a href='${link}'><p style='padding-left:60px;' class='tool_tip' title='click to see original post in Google+'>${title}</p></a>"\
                    "<ul style='padding-left:60px;' class='actions'></ul>"\
                "</li>"

    def generate_configured_guid(self, config):
        base_string = ' '.join([e['value'] for e in config['elements']])
        return md5(base_string).hexdigest()

    def generate_configured_display_name(self, config):
        keywords = [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']
        return '%s: %s' % (config['display_name_short'], keywords)

    def validate_config(self, config):
        keywords = [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']

        errors = { 'keywords':[] }
        if not keywords or not keywords.strip():
            errors['keywords'].append('You must search for something.')

        if errors['keywords']:
            return False, errors
        return True, {}

    def oauth_get_oauth2_return_handler(self, data_point_id):
        flow = self.flow
        flow.params['state'] = '_'.join([data_point_id, self.get_unconfigured_config()['type']])
        return flow

    def oauth_credentials_are_valid(self, credentials_json):
        if not credentials_json:
            return False
        try:
            credentials = Credentials.new_from_json(credentials_json)
        except Exception:
            return False
        if credentials is None or credentials.invalid:
            return False
        return True

    def oauth_poll_for_new_credentials(self, config):
        credentials = GoogleOauth2Controller.PollForNewCredentials(self.oauth_get_oauth2_return_handler(config['id']))
        if not credentials:
            return None
        oauth_element = [e for e in config['elements'] if e['name'] == 'oauth2'][0]
        oauth_element['value'] = credentials.to_json()
        return config

    def oauth_get_oauth_authenticate_url(self, id):
        authorize_url = GoogleOauth2Controller.GetOauth2AuthorizationUrl(self.oauth_get_oauth2_return_handler(id))
        return authorize_url

    def tick(self, config):
        Logger.Info('%s - tick - started - with config: %s' % (__name__, config))
        keywords = [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']
        credentials = Credentials.new_from_json([e for e in config['elements'] if e['name'] == 'oauth2'][0]['value'])
        http = credentials.authorize(httplib2.Http())
        service = build('plus', 'v1', http=http)
        response = service.activities().search(query=keywords).execute()
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
