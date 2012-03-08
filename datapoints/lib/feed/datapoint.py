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
            'type':'feed',
            'sub_type':'feed',
            'display_name_short':'Feed',
            'full_display_name':'Web Feed (rss/atom)',
            'instructions':'Use this data point to subscribe to any web feed published using either rss or atom syndication.',
            'image_large':'/static/images/thedashboard/data_points/feed_large.png',
            'image_medium':'/static/images/thedashboard/data_points/feed_medium.png',
            'image_small':'/static/images/thedashboard/data_points/feed_small.png',
            'configured':False,
            'elements':[
                {
                    'name':'url',
                    'display_name':'The feed url',
                    'help':'The full url of the feed you want to subscribe to',
                    'type':'text',
                    'value':''
                }
            ]
        }

    def get_content_item_template(self):
        return "" \
            "<li style='width:100%;'>" \
                "<img src='/static/images/lib/yoo/feed_2424.png' style='width:20px; padding-right:10px;' align='left'/>"\
                "<p style='float:right;padding-right:10px;'>${pretty_date}</p>"\
                "<p style='margin-bottom:2px;'>${source_display_name}</p>" \
                "<p style='padding-left:30px;'>${author_display_name}<span style='font-weight:bold'> ${title}</span></p>" \
            "</li>"

    def generate_configured_guid(self, config):
        url = [e for e in config['elements'] if e['name'] == 'url'][0]['value']
        return md5(url).hexdigest()

    def generate_configured_display_name(self, config):
        url = [e for e in config['elements'] if e['name'] == 'url'][0]['value']
        parsed_url = urlparse(url)
        return 'Web Feed: %s%s' % (parsed_url.netloc, parsed_url.path)

    def validate_config(self, config):
        url = [e for e in config['elements'] if e['name'] == 'url'][0]['value']
        if not url or url == '':
            return False, { 'url':['Url can not be empty'] }
        parsed_url = urlparse(url)
        if parsed_url.netloc == '':
            return False, { 'url':['The url did not parse correctly, it must be a full url'] }
        feed = feedparser.parse(url)
        if not feed['feed']:
            return False, { 'url':['This url does not seem to point to a feed?'] }
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
