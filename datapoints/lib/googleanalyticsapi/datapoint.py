import datetime
import re
import time
from metalayercore.datapoints.classes import BaseDataPoint
from dateutil import parser as dateutil_parser, tz
from urlparse import urlparse
from hashlib import md5
import feedparser
from logger import Logger

class DataPoint(BaseDataPoint):
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
                    'name':'url',
                    'display_name':'The feed url',
                    'help':'The full url of the feed you want to subscribe to',
                    'type':'text',
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
