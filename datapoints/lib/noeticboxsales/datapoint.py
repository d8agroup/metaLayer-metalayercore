import os
import time
import datetime
from hashlib import md5
from metalayercore.datapoints.classes import BaseDataPoint


class DataPoint(BaseDataPoint):
    def get_unconfigured_config(self):
        start_date = datetime.datetime(2012, 3, 19)
        end_date = datetime.datetime(2013, 4, 4)
        return {
            'type': 'noeticboxsales',
            'sub_type': 'noeticboxsales',
            'is_live': False,
            'display_name_short': 'Sales Data',
            'full_display_name': 'Sales Data',
            'instructions': """Use this datapoint to access Shoptiques sales data.""",
            'image_large': 'http://www.shoptiques.com/static/QkwNhENd2YYKTVxudSE9Wj5XzTgJACaYfk48sY07cIg.ico',
            'image_medium': 'http://www.shoptiques.com/static/QkwNhENd2YYKTVxudSE9Wj5XzTgJACaYfk48sY07cIg.ico',
            'image_small': 'http://www.shoptiques.com/static/QkwNhENd2YYKTVxudSE9Wj5XzTgJACaYfk48sY07cIg.ico',
            'configured': True,
            'elements': [
                self._generate_base_search_start_time_config_element(start_time=time.mktime(start_date.timetuple())),
                self._generate_base_search_end_time_config_element(end_time=time.mktime(end_date.timetuple()))],
            'meta_data': [
                {'display_name': 'User Id', 'name': 'extensions_userid_s', 'type': 'string'},
                {'display_name': 'User Registered Date', 'name': 'extensions_userregistereddate_s', 'type': 'string'},
                {'display_name': 'Email Address', 'name': 'extensions_useremail_s', 'type': 'string'},
                {'display_name': 'First Name', 'name': 'extensions_userfirstname_s', 'type': 'string'},
                {'display_name': 'Surname', 'name': 'extensions_usersurname_s', 'type': 'string'},
                {'display_name': 'Date in Cart', 'name': 'extensions_dateincart_s', 'type': 'string'},
                {'display_name': 'Status', 'name': 'extensions_status_s', 'type': 'string'},
                {'display_name': 'Product Url', 'name': 'extensions_producturl_s', 'type': 'string'},
                {'display_name': 'Product Amount', 'name': 'extensions_productamount_f', 'type': 'float'},
                {'display_name': 'Product Color', 'name': 'extensions_productcolor_s', 'type': 'string'},
                {'display_name': 'Product Size', 'name': 'extensions_productsize_s', 'type': 'string'},
                {'display_name': 'Boutique', 'name': 'extensions_boutique_s', 'type': 'string'},
                {'display_name': 'Label', 'name': 'extensions_label_s', 'type': 'string'},
                {'display_name': 'Order ID', 'name': 'extensions_orderid_s', 'type': 'string'},
                {'display_name': 'Date Order Created', 'name': 'extensions_ordercreateddate_s', 'type': 'string'},
                {'display_name': 'Promo Code', 'name': 'extensions_promocode_s', 'type': 'string'},
                {'display_name': 'Link Share', 'name': 'extensions_linkshare_s', 'type': 'string'},
                {'display_name': 'Order Total', 'name': 'extensions_ordertotal_f', 'type': 'float'},
                {'display_name': 'Order Items Count', 'name': 'extensions_orderitemscount_f', 'type': 'float'},
                {'display_name': 'Channel', 'name': 'extensions_channel_s', 'type': 'string'},
            ]
        }

    def get_content_item_template(self):
        template_path = os.path.dirname(os.path.abspath(__file__)) + "/template.html"
        with open(template_path, "rb") as f:
            template = f.read().replace("\n", "")
        return template

    def generate_configured_guid(self, config):
        base_string = 'noeticboxsales_v01_source'
        return md5(base_string).hexdigest()

    def generate_configured_display_name(self, config):
        return "Sales Data"

    def validate_config(self, config):
        return True, {}

    def tick(self, config):
        return