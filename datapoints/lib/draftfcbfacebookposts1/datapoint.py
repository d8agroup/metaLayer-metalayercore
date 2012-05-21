from hashlib import md5
import datetime
import time
from metalayercore.datapoints.classes import BaseDataPoint

class DataPoint(BaseDataPoint):
    def get_unconfigured_config(self):
        return {
            'type':'draftfcbfacebookposts1',
            'sub_type':'draftfcbfacebookposts1',
            'display_name_short':'Facebook Posts',
            'full_display_name':'Draft FCB Facebook Posts Data',
            'instructions':'Use this data point to search facebook posts collected from Sysomos.',
            'image_large':'/static/images/thedashboard/data_points/facebook_medium.png',
            'image_medium':'/static/images/thedashboard/data_points/facebook_medium.png',
            'image_small':'/static/images/thedashboard/data_points/facebook_small.png',
            'configured':True,
            'elements':[
                self._generate_base_search_start_time_config_element(time.mktime(datetime.datetime(2012, 3, 1, 0, 0, 0).timetuple())),
                self._generate_base_search_end_time_config_element(time.mktime(datetime.datetime(2012, 5, 1, 0, 0, 0).timetuple()))
            ],
            'meta_data':[
                {
                    'display_name':'Lifetime Engaged Users',
                    'name':'extensions_LifetimeEngagedUsers_f',
                    'type':'float'
                },
                {
                    'display_name':'Lifetime Post Organic Reach',
                    'name':'extensions_LifetimePostOrganicReach_f',
                    'type':'float'
                }
            ]
        }

    def get_content_item_template(self):
        return ""\
               "<li style='width:100%;'>"\
               "<img src='/static/images/thedashboard/data_points/facebook_small.png' style='width:20px; padding-right:10px;' align='left'/>"\
               "<p style='float:right;padding-right:10px;'>${pretty_date}</p>"\
               "<p style='margin-bottom:2px;'>${source_display_name}</p>"\
               "<p style='padding-left:30px;'>${author_display_name}<span style='font-weight:bold'> ${title}</span></p>"\
               "<ul style='padding-left:30px;' class='actions'>"\
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Lifetime Engaged Users</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_range_filter' data-facet_name='extensions_LifetimeEngagedUsers_f' data-facet_value='${extensions_LifetimeEngagedUsers_f}'>${parseInt(extensions_LifetimeEngagedUsers_f)}</a>"\
               "       </span>"\
               "    </li>" \
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Lifetime Post Organic Reach</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_range_filter' data-facet_name='extensions_LifetimePostOrganicReach_f' data-facet_value='${extensions_LifetimePostOrganicReach_f}'>${parseInt(extensions_LifetimePostOrganicReach_f)}</a>"\
               "       </span>"\
               "    </li>" \
               "</ul>"\
               "</li>"
#               "    {{if extensions_age_s}}"\
#               "    <li class='action_values' style='margin-top:5px;'>"\
#               "       <label>Age</label>"\
#               "       <span style='font-weight:bold;'>"\
#               "           <a class='action_inline_filter' data-facet_name='extensions_age_s' data-facet_value='${extensions_age_s}'>${extensions_age_s}</a>"\
#               "       </span>"\
#               "    </li>" \
#               "    {{/if}}"\
#               "    {{if extensions_gender_s}}"\
#               "    <li class='action_values' style='margin-top:5px;'>"\
#               "       <label>Gender</label>"\
#               "       <span style='font-weight:bold;'>"\
#               "           <a class='action_inline_filter' data-facet_name='extensions_gender_s' data-facet_value='${extensions_gender_s}'>${extensions_gender_s}</a>"\
#               "       </span>"\
#               "    </li>" \
#               "    {{/if}}"\
#               "    {{if extensions_country_s}}"\
#               "    <li class='action_values' style='margin-top:5px;'>"\
#               "       <label>Country</label>"\
#               "       <span style='font-weight:bold;'>"\
#               "           <a class='action_inline_filter' data-facet_name='extensions_country_s' data-facet_value='${extensions_country_s}'>${extensions_country_s}</a>"\
#               "       </span>"\
#               "    </li>" \
#               "    {{/if}}"\
#               "</ul>"\
#               "</li>"

    def generate_configured_guid(self, config):
        base_string = 'draftfcbfacebookposts1_source'
        return md5(base_string).hexdigest()

    def generate_configured_display_name(self, config):
        return config['full_display_name']

    def validate_config(self, config):
        return True, {}

    def tick(self, config):
        return []