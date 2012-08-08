import datetime
from django.conf import settings
from apiclient.discovery import build
import httplib2
from oauth2client.client import  OAuth2WebServerFlow, Credentials
import re
import time
from metalayercore.datapoints.classes import BaseDataPoint
from dateutil import parser as dateutil_parser, tz
from urlparse import urlparse
from hashlib import md5
import feedparser
from logger import Logger
from metalayercore.oauth2bridge.controllers import GoogleOauth2Controller

class DataPoint(BaseDataPoint):
    flow = OAuth2WebServerFlow(
        client_id="THIS IS MANAGED ELSEWHERE",
        client_secret="THIS IS MANAGED ELSEWHERE",
        scope='https://www.googleapis.com/auth/analytics.readonly',
        redirect_uri='THIS IS MANAGED ELSEWHERE')

    def get_unconfigured_config(self):
        return {
            'type':'googleanalyticsapi',
            'sub_type':'googleanalyticsapi',
            'display_name_short':'Google Analytics',
            'full_display_name':'Google Analytics API',
            'instructions':'Use this data point to access your data in Google Analytics.',
            'image_large':'/static/images/thedashboard/data_points/ga_large.png',
            'image_medium':'/static/images/thedashboard/data_points/ga_medium.png',
            'image_small':'/static/images/thedashboard/data_points/ga_small.png',
            'configured':False,
            'elements':[
                {
                    'name':'account',
                    'display_name':'The Google Analytics Account to get data from.',
                    'help':'',
                    'type':'select',
                    'value':'',
                    'values':[
                    ]
                },
                {
                    'name':'oauth2',
                    'display_name':'oauth2',
                    'help':'',
                    'type':'oauth2',
                    'value':''
                },
                self._generate_base_search_start_time_config_element(start_time=time.mktime((datetime.datetime.utcnow() - datetime.timedelta(hours=6)).timetuple())),
                self._generate_base_search_end_time_config_element()
            ]
        }

    def get_content_item_template(self):
        return "" \
            "<li style='width:100%;'>" \
                "<img src='/static/images/thedashboard/data_points/feed_small.png' style='width:20px; padding-right:10px;' align='left'/>"\
                "<p style='float:right;padding-right:10px;'>${pretty_date}</p>"\
                "<p style='margin-bottom:2px;'>${source_display_name}</p>" \
                "<p style='padding-left:30px;'>${author_display_name}<span style='font-weight:bold'> ${title}</span></p>" \
                "<ul style='padding-left:30px;' class='actions'></ul>" \
            "</li>"

    def generate_configured_guid(self, config):
        url = [e for e in config['elements'] if e['name'] == 'url'][0]['value']
        return md5(url).hexdigest()

    def generate_configured_display_name(self, config):
        url = [e for e in config['elements'] if e['name'] == 'url'][0]['value']
        parsed_url = urlparse(url)
        return 'Google Analytics: %s%s' % (parsed_url.netloc, parsed_url.path)

    def validate_config(self, config):
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
        oauth_element = [e for e in config['elements'] if e['name'] == 'oauth2'][0]
        oauth_element['value'] = credentials.to_json()
        return config

    def oauth_get_oauth_authenticate_url(self, id):
        authorize_url = GoogleOauth2Controller.GetOauth2AuthorizationUrl(self.oauth_get_oauth2_return_handler(id))
        return authorize_url

    def update_data_point_with_oauth_dependant_config(self, config):
        credentials = Credentials.new_from_json([e for e in config['elements'] if e['name'] == 'oauth2'][0]['value'])
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('analytics', 'v3', http=http)
        accounts = service.management().accounts().list().execute()
        accounts = accounts.get('items')
        accounts = sorted(accounts, key=lambda a: a['updated'], reverse=True)
        accounts_element = [e for e in config['elements'] if e['name'] == 'account'][0]

        post_oauth_request_accounts = [{'value': a.get('id'), 'name': a.get('name')} for a in accounts if 'id' in a and 'name' in a]
        accounts_element['values'] = post_oauth_request_accounts

        oauth2_element = [e for e in config['elements'] if e['name'] == 'oauth2'][0]
        oauth2_element['value'] = credentials.to_json()

        return config

    def tick(self, config):
        Logger.Info('%s - tick - started - with config: %s' % (__name__, config))
        feed_url = [e for e in config['elements'] if e['name'] == 'url'][0]['value']
        feed = feedparser.parse(feed_url)
        content = [self._map_feed_item_to_content_item(config, item) for item in feed['items']]
        Logger.Info('%s - tick - finished' % __name__)
        return content

    def _map_feed_item_to_content_item(self, config, item):
        return {
            'id':md5(item['link']).hexdigest(),
            'text':[
                    {
                    'title': item['title'],
                    'text':[
                        re.sub(r'<.*?>', '', item['summary'])
                    ],
                    'tags':[t['term'] for t in item['tags']] if 'tags' in item else []
                }
            ],
            'time': time.mktime(dateutil_parser.parse(item['updated']).astimezone(tz.tzutc()).timetuple()),
            'link':item['link'],
            'author':{
                'display_name':item['author'] if 'author' in item else 'none',
                },
            'channel':{
                'id':md5(config['type'] + config['sub_type'] if 'sub_type' in config else '').hexdigest(),
                'type':config['type'],
                'sub_type':config['sub_type'] if 'sub_type' in config else None
            },
            'source':{
                'id':self.generate_configured_guid(config),
                'display_name':self.generate_configured_display_name(config),
                }
        }

    def _clean_url_for_display_name(self, url):
        parsed_url = urlparse.urlparse(url)
        return parsed_url.netloc + '-'.join(parsed_url.path.split('/'))