from hashlib import md5
import datetime
import time
from metalayercore.datapoints.classes import BaseDataPoint

class DataPoint(BaseDataPoint):
    def get_unconfigured_config(self):
        return {
            'type':'draftfcbblogs1',
            'sub_type':'draftfcbblogs1',
            'display_name_short':'Blogs',
            'full_display_name':'Draft FCB Blog Data',
            'instructions':'Use this data point to search blogs collected from Sysomos.',
            'image_large':'/static/images/thedashboard/data_points/feed_large.png',
            'image_medium':'/static/images/thedashboard/data_points/feed_medium.png',
            'image_small':'/static/images/thedashboard/data_points/feed_small.png',
            'configured':True,
            'elements':[
                self._generate_base_search_start_time_config_element(time.mktime(datetime.datetime(2012, 3, 1, 0, 0, 0).timetuple())),
                self._generate_base_search_end_time_config_element(time.mktime(datetime.datetime(2012, 5, 1, 0, 0, 0).timetuple()))
            ],
            'meta_data':[
                {
                    'display_name':'Sentiment',
                    'name':'extensions_sentiment_s',
                    'type':'string'
                },
                {
                    'display_name':'Age',
                    'name':'extensions_age_s',
                    'type':'string'
                },
                {
                    'display_name':'Gender',
                    'name':'extensions_gender_s',
                    'type':'string'
                },
                {
                    'display_name':'Country',
                    'name':'extensions_country_s',
                    'type':'string'
                },
            ]
        }

    def get_content_item_template(self):
        return ""\
               "<li style='width:100%;'>"\
               "<img src='/static/images/thedashboard/data_points/feed_small.png' style='width:20px; padding-right:10px;' align='left'/>"\
               "<p style='float:right;padding-right:10px;'>${pretty_date}</p>"\
               "<p style='margin-bottom:2px;'>${source_display_name}</p>"\
               "<p style='padding-left:30px;'>${author_display_name}<span style='font-weight:bold'> ${title} - ${display_text_abstract(text)}</span></p>"\
               "<ul style='padding-left:30px;' class='actions'>"\
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Sentiment</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_filter' data-facet_name='extensions_sentiment_s' data-facet_value='${extensions_sentiment_s}'>${extensions_sentiment_s}</a>"\
               "       </span>"\
               "    </li>" \
               "    {{if extensions_age_s}}"\
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Age</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_filter' data-facet_name='extensions_age_s' data-facet_value='${extensions_age_s}'>${extensions_age_s}</a>"\
               "       </span>"\
               "    </li>" \
               "    {{/if}}"\
               "    {{if extensions_gender_s}}"\
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Gender</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_filter' data-facet_name='extensions_gender_s' data-facet_value='${extensions_gender_s}'>${extensions_gender_s}</a>"\
               "       </span>"\
               "    </li>" \
               "    {{/if}}"\
               "    {{if extensions_country_s}}"\
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Country</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_filter' data-facet_name='extensions_country_s' data-facet_value='${extensions_country_s}'>${extensions_country_s}</a>"\
               "       </span>"\
               "    </li>" \
               "    {{/if}}"\
               "</ul>"\
               "</li>"

    def generate_configured_guid(self, config):
        base_string = 'draftfcbblogs1_source'
        return md5(base_string).hexdigest()

    def generate_configured_display_name(self, config):
        return config['full_display_name']

    def validate_config(self, config):
        return True, {}

    def tick(self, config):
        return []