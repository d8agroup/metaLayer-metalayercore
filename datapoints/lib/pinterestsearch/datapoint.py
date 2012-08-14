import os
import lxml.etree
from hashlib import md5
from urllib import quote
from urllib2 import urlopen
from logger import Logger
from metalayercore.datapoints.classes import BaseDataPoint


class DataPoint(BaseDataPoint):
    def get_unconfigured_config(self):
        return {
            'type': 'pinterestsearch',
            'sub_type': 'pinterestsearch',
            'is_live': True,
            'display_name_short': 'Pinterest',
            'full_display_name': 'Pinterest Search',
            'instructions': 'Use this data point to search Pinterest\'s public data.',
            'image_large': '/static/images/thedashboard/data_points/pinterest_large.png',
            'image_medium': '/static/images/thedashboard/data_points/pinterest_medium.png',
            'image_small': '/static/images/thedashboard/data_points/pinterest_small.png',
            'configured': False,
            'elements': [
                {
                    'name': 'keywords',
                    'display_name': 'What to search for',
                    'help': 'The keywords that you want to use to search Pinterest',
                    'type': 'text',
                    'value': ''
                },
                self._generate_base_search_start_time_config_element(),
                self._generate_base_search_end_time_config_element(),
            ],
            'meta_data': [
                {
                    'display_name':'Pinterest Username',
                    'name':'extensions_username_s',
                    'type':'string'
                },{
                    'display_name': 'Pins',
                    'name': 'extensions_repins_f',
                    'type': 'float'
                },{
                    'display_name': 'Likes',
                    'name': 'extensions_likes_f',
                    'type': 'float'
                },{
                    'display_name': 'Comments',
                    'name': 'extensions_comments_f',
                    'type': 'float'
                }
            ]
        }

    def get_content_item_template(self):
        """Fetch HTML from external template but checking cache first.
        XXX: Be sure to disable this during development.
        """

        tpl_path = os.path.dirname(os.path.abspath(__file__)) + "/template.html"
        tpl_key = md5(tpl_path).hexdigest()
        tpl = self.cache_get(tpl_key)

        if not tpl:
            with open(tpl_path, "rb") as f:
                tpl = f.read().replace("\n", "")
                self.cache_add(tpl_key, tpl, timeout=10*60)

        return tpl

    def generate_configured_guid(self, config):
        base_string = 'pinterest_search %s' % [e for e in config['elements'] if e['name'] == 'keywords'][0]['value']
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

        url = "http://pinterest.com/search/?q=%s" % keywords
        response = urlopen(url).read()
        Logger.Debug('%s - tick - raw response: %s' % (__name__, response))

        doc = lxml.etree.fromstring(response, lxml.etree.HTMLParser())
        pins = doc.xpath("/html/body//div[@class='pin']")

        content = [self._map_pinterest_item_to_content_item(config, item) for item in pins]

        Logger.Info('%s - tick - finished' % __name__)
        return content

    def _map_pinterest_item_to_content_item(self, config, item):

        # XXX: These XPath queries are hella brittle
        pin_id = item.attrib['data-id']
        link = "http://pinterest.com" + item.xpath('.//a[@class="PinImage ImgLink"]//@href')[0]
        image = item.xpath('.//a[@class="PinImage ImgLink"]//@src')[0]
        text = item.xpath('.//p[@class="description"]/text()')[0]

        user_node = item.xpath('.//div[contains(@class, "attribution")]')[0]
        user_name = user_node.xpath('.//a//@title')[0]
        user_link = "http://pinterest.com" + user_node.xpath('.//a//@href')[0]
        user_image = user_node.xpath('.//a//img//@src')[0]

        repins = item.xpath('.//p[contains(@class, "stats")]//span[@class="RepinsCount"]/text()')
        if repins:
            repins = int(repins[0].strip().split(' ')[0])
        else:
            repins = 0

        likes = item.xpath('.//p[contains(@class, "stats")]//span[@class="LikesCount"]/text()')
        if likes:
            likes = int(likes[0].strip().split(' ')[0])
        else:
            likes = 0

        comments = item.xpath('.//p[contains(@class, "stats")]//span[@class="CommentsCount"]/text()')
        if comments:
            comments = int(comments[0].strip().split(' ')[0])
        else:
            comments = 0

        return {
            'id': md5(str(pin_id)).hexdigest(),
            'link': link,
            'text': [{ 'text': text }],
            'image_s': image,
            'time': 2**32, # XXX: Workaround for the last successful run filter
            'author': {
                'display_name': user_name,
                'link': user_link,
                'image': user_image
            },
            'channel': {
                'id': md5(config['type'] + config['sub_type']).hexdigest(),
                'type': config['type'],
                'sub_type': config['sub_type']
            },
            'source': {
                'id': self.generate_configured_guid(config),
                'display_name': self.generate_configured_display_name(config),
            },
            'extensions': {
                'username': {
                    'type': 'string',
                    'value': user_name
                },
                'repins': {
                    'type': 'float',
                    'value': repins
                },
                'likes': {
                    'type': 'float',
                    'value': likes
                },
                'comments': {
                    'type': 'float',
                    'value': comments
                }
            }
        }
