from hashlib import md5
from urllib import quote
import urlparse
import re
from metalayercore.datapoints.classes import BaseDataPoint
from logger import Logger
from dateutil import parser as dateutil_parser, tz
import feedparser
import time

class DataPoint(BaseDataPoint):
    def get_unconfigured_config(self):
        return {
            'type':'googlenewssearch',
            'sub_type':'googlenewssearch',
            'display_name_short':'Google News',
            'full_display_name':'Google News',
            'instructions':'Use this data point to search Google news.',
            'image_large':'/static/images/thedashboard/data_points/googlenews_large.png',
            'image_medium':'/static/images/thedashboard/data_points/googlenews_medium.png',
            'image_small':'/static/images/thedashboard/data_points/googlenews_small.png',
            'configured':False,
            'elements':[
                {
                    'name':'keywords',
                    'display_name':'What to search for',
                    'help':'The keywords that you want to use to search Google News',
                    'type':'text',
                    'value':''
                },
            ]
        }

    def get_content_item_template(self):
        return ""\
               "<li style='width:100%;'>"\
                   "<img src='/static/images/lib/yoo/google_2424.png' style='width:20px; padding-right:10px;' align='left'/>" \
                   "<p style='float:right;padding-right:10px;'>${pretty_date}</p>"\
                   "<p style='margin-bottom:2px;'>${source_display_name} - ${action_localsentimentanalysis_sentiment_s}</p>"\
                   "<a href='${link}' class='tool_tip' title='click to view the original article'><p style='padding-left:30px;'>${author_display_name}<span style='font-weight:bold'> ${title}</span></p></a>" \
               "</li>"

    def generate_configured_guid(self, config):
        base_string = 'google_news_search %s' % [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']
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
        url = 'http://news.google.com/news?hl=en&gl=us&q=%s&safe=on&output=rss' % keywords
        feed = feedparser.parse(url)
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
