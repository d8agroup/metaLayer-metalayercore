import calendar
from metalayercore.oauth2bridge.controllers import GoogleOauth2Controller
from oauth2client.client import  OAuth2WebServerFlow, Credentials
from metalayercore.datapoints.classes import BaseDataPoint
from apiclient.discovery import build
from hashlib import md5
import httplib2
import datetime
import time

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
                    'name':'oauth2',
                    'display_name':'oauth2',
                    'help':"""To access your data from Google Analytics, you need to authorize Delv to collect data on your
                              behalf.<br/><br/>
                              Please click the Authorize button below, you will then be take to a Google web page so you can
                              authorize Delv.""",
                    'type':'oauth2',
                    'value':''
                },
                {
                    'name':'account',
                    'display_name':'Google Analytics Account',
                    'help':'The Google Analytics Account to get data from.',
                    'type':'select',
                    'value':'',
                    'values':[
                    ]
                },
                {
                    'name':'metrics',
                    'display_name':'Metrics to include (max 10)',
                    'help':'Choose the metrics you want to bring in to from Google Analytics up to a maximum of 10.',
                    'type':'multiple_select',
                    'value':'',
                    'values':[
                        {'name':'Visitors', 'value':'ga:visitors', 'option_group':'Visitor'},
                        {'name':'New Visits', 'value':'ga:newVisits', 'option_group':'Visitor'},
                        {'name':'Visits', 'value':'ga:visits', 'option_group':'Session'},
                        {'name':'Bounces', 'value':'ga:bounces', 'option_group':'Session'},
                        {'name':'Visit Bounce Rate', 'value':'ga:visitBounceRate', 'option_group':'Session'},
                        {'name':'Organic Searches', 'value':'ga:organicSearches', 'option_group':'Traffic Sources'},
                        {'name':'Page Views', 'value':'ga:pageviews', 'option_group':'Page Tracking'},
                        {'name':'Page Views per Visit', 'value':'ga:pageviewsPerVisit', 'option_group':'Page Tracking'},
                        {'name':'Unique Page Views', 'value':'ga:uniquePageviews', 'option_group':'Page Tracking'},
                    ]
                },
                {
                    'name':'start_date',
                    'display_name':'Start Date',
                    'help':'',
                    'type':'date_time',
                    'value':(datetime.datetime.now() + datetime.timedelta(-30)).strftime("%d/%m/%Y"),
                },
                {
                    'name':'end_date',
                    'display_name':'End Date',
                    'help':'',
                    'type':'date_time',
                    'value':datetime.datetime.now().strftime("%d/%m/%Y"),
                },
                self._generate_base_search_start_time_config_element(start_time=time.mktime((datetime.datetime.utcnow() - datetime.timedelta(hours=1)).timetuple())),
                self._generate_base_search_end_time_config_element()
            ],
            'meta_data':[
                { 'display_name':'Total Visitors', 'name':'extensions_visitors_f', 'type':'float' },
                { 'display_name':'Visitors', 'name':'extensions_newVisits_f', 'type':'float' },
                { 'display_name':'Visits', 'name':'extensions_visits_f', 'type':'float' },
                { 'display_name':'Bounces', 'name':'extensions_bounces_f', 'type':'float' },
                { 'display_name':'Visit Bounce Rate', 'name':'extensions_visitBounceRate_f', 'type':'float' },
                { 'display_name':'Organic Searches', 'name':'extensions_organicSearches_f', 'type':'float'},
                { 'display_name':'Page Views', 'name':'extensions_pageviews_f', 'type':'float'},
                { 'display_name':'Page Views per Visit', 'name':'extensions_pageviewsPerVisit_f', 'type':'float'},
                { 'display_name':'Unique Page Views', 'name':'extensions_uniquePageviews_f', 'type':'float'},
            ]
        }

    def get_content_item_template(self):
        return "" \
            "<li style='width:100%;'>" \
                "<img src='/static/images/thedashboard/data_points/ga_small.png' style='width:20px; padding-right:10px;' align='left'/>"\
                "<p style='padding-left:30px;'><span style='font-weight:bold'> ${title}</span></p>"\
                "<ul style='padding-left:30px;' class='actions'>" \
                "   {{if (typeof extensions_visitors_f !== 'undefined')}}"\
                "    <li class='action_values' style='margin-top:2px; display:inline-block; width:32%;'>"\
                "       <label>Visitors</label>"\
                "       <span style='font-weight:bold;'>"\
                "           <a class='action_inline_range_filter' data-facet_name='extensions_visitors_f' data-facet_value='${extensions_visitors_f}'>${extensions_visitors_f}</a>"\
                "       </span>" \
                "   </li>" \
                "   {{/if}}"\
                "   {{if (typeof extensions_newVisits_f !== 'undefined')}}"\
                "    <li class='action_values' style='margin-top:2px; display:inline-block; width:32%;'>"\
                "       <label>New Visits</label>"\
                "       <span style='font-weight:bold;'>"\
                "           <a class='action_inline_range_filter' data-facet_name='extensions_newVisits_f' data-facet_value='${extensions_newVisits_f}'>${extensions_newVisits_f}</a>"\
                "       </span>" \
                "   </li>" \
                "   {{/if}}"\
                "   {{if (typeof extensions_visits_f !== 'undefined')}}"\
                "    <li class='action_values' style='margin-top:2px; display:inline-block; width:32%;'>"\
                "       <label>Visits</label>"\
                "       <span style='font-weight:bold;'>"\
                "           <a class='action_inline_range_filter' data-facet_name='extensions_visits_f' data-facet_value='${extensions_visits_f}'>${extensions_visits_f}</a>"\
                "       </span>" \
                "   </li>" \
                "   {{/if}}"\
                "   {{if (typeof extensions_bounces_f !== 'undefined')}}"\
                "    <li class='action_values' style='margin-top:2px; display:inline-block; width:32%;'>"\
                "       <label>Bounces</label>"\
                "       <span style='font-weight:bold;'>"\
                "           <a class='action_inline_range_filter' data-facet_name='extensions_bounce_f' data-facet_value='${extensions_bounces_f}'>${extensions_bounces_f}</a>"\
                "       </span>" \
                "   </li>" \
                "   {{/if}}"\
                "   {{if (typeof extensions_visitBounceRate_f !== 'undefined')}}"\
                "    <li class='action_values' style='margin-top:2px; display:inline-block; width:32%;'>"\
                "       <label>Visit Bounce Rate</label>"\
                "       <span style='font-weight:bold;'>"\
                "           <a class='action_inline_range_filter' data-facet_name='extensions_visitBounceRate_f' data-facet_value='${extensions_visitBounceRate_f}'>${extensions_visitBounceRate_f}&#37;</a>"\
                "       </span>" \
                "   </li>" \
                "   {{/if}}"\
                "   {{if (typeof extensions_organicSearches_f !== 'undefined')}}"\
                "    <li class='action_values' style='margin-top:2px; display:inline-block; width:32%;'>"\
                "       <label>Organic Searches</label>"\
                "       <span style='font-weight:bold;'>"\
                "           <a class='action_inline_range_filter' data-facet_name='extensions_organicSearches_f' data-facet_value='${extensions_organicSearches_f}'>${extensions_organicSearches_f}</a>"\
                "       </span>" \
                "   </li>" \
                "   {{/if}}"\
                "   {{if (typeof extensions_pageviews_f !== 'undefined')}}"\
                "    <li class='action_values' style='margin-top:2px; display:inline-block; width:32%;'>"\
                "       <label>Page Views</label>"\
                "       <span style='font-weight:bold;'>"\
                "           <a class='action_inline_range_filter' data-facet_name='extensions_pageviews_f' data-facet_value='${extensions_pageviews_f}'>${extensions_pageviews_f}</a>"\
                "       </span>" \
                "   </li>" \
                "   {{/if}}"\
                "   {{if (typeof extensions_pageviewsPerVisit_f !== 'undefined')}}"\
                "    <li class='action_values' style='margin-top:2px; display:inline-block; width:32%;'>"\
                "       <label>Page Views Per Visit</label>"\
                "       <span style='font-weight:bold;'>"\
                "           <a class='action_inline_range_filter' data-facet_name='extensions_pageviewsPerVisit_f' data-facet_value='${extensions_pageviewsPerVisit_f}'>${extensions_pageviewsPerVisit_f}</a>"\
                "       </span>" \
                "   </li>" \
                "   {{/if}}"\
                "   {{if (typeof extensions_uniquePageviews_f !== 'undefined')}}"\
                "    <li class='action_values' style='margin-top:2px; display:inline-block; width:32%;'>"\
                "       <label>Unique Page Views</label>"\
                "       <span style='font-weight:bold;'>"\
                "           <a class='action_inline_range_filter' data-facet_name='extensions_uniquePageviews_f' data-facet_value='${extensions_uniquePageviews_f}'>${extensions_uniquePageviews_f}</a>"\
                "       </span>" \
                "   </li>" \
                "   {{/if}}"\
                "</ul>"\
                "</li>"

    def generate_configured_guid(self, config):
        id = config.get('id')
        if id:
            return id
        account_id = [e for e in config['elements'] if e['name'] == 'account'][0]['value']
        return md5('%s %i' % (account_id, int(time.time()))).hexdigest()

    def generate_configured_display_name(self, config):
        account_element = [e for e in config['elements'] if e['name'] == 'account'][0]
        account_id = account_element['value']
        account_name = [v['name'] for v in account_element['values'] if v['value'] == account_id][0]
        return 'Google Analytics: %s' % account_name

    def validate_config(self, config):
        metrics_element = [e for e in config['elements'] if e['name'] == 'metrics'][0]
        if not metrics_element['value']:
            return False, { 'metrics':['You must choose some metrics to collect'] }
        number_of_metrics_chosen = len(metrics_element['value'])
        if number_of_metrics_chosen > 10:
            return False, { 'metrics':['You have chosen %i metrics, the limit is 10' % number_of_metrics_chosen] }
        return True, {}

    def perform_post_validation_configuration_changes(self, config):
        """
        Take the date strings entered into the data point config and set the start and end time elements
        """
        start_date = [e for e in config['elements'] if e['name'] == 'start_date'][0]['value']
        start_time_element = [e for e in config['elements'] if e['name'] == 'start_time'][0]
        start_time_element['value'] = '%i' % calendar.timegm(datetime.datetime.strptime(start_date, '%d/%m/%Y').timetuple())
        end_date = [e for e in config['elements'] if e['name'] == 'end_date'][0]['value']
        end_time_element = [e for e in config['elements'] if e['name'] == 'end_time'][0]
        end_time_element['value'] = '%i' % calendar.timegm(datetime.datetime.strptime(end_date, '%d/%m/%Y').timetuple())
        return config

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

    def update_data_point_with_oauth_dependant_config(self, config):
        def get_profile_id_for_account(service, account_id):
            web_properties = service.management().webproperties().list(accountId=account_id).execute()
            web_property_id = web_properties.get('items')[0].get('id')
            profiles = service.management().profiles().list(accountId=account_id,webPropertyId=web_property_id).execute()
            return profiles.get('items')[0].get('id')

        credentials = Credentials.new_from_json([e for e in config['elements'] if e['name'] == 'oauth2'][0]['value'])
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('analytics', 'v3', http=http)
        accounts = service.management().accounts().list().execute()
        accounts = accounts.get('items')
        accounts = sorted(accounts, key=lambda a: a['updated'], reverse=True)
        accounts_element = [e for e in config['elements'] if e['name'] == 'account'][0]
        post_oauth_request_accounts = [{'value': get_profile_id_for_account(service, a.get('id')), 'name': a.get('name')} for a in accounts if 'id' in a and 'name' in a]
        accounts_element['values'] = post_oauth_request_accounts
        oauth2_element = [e for e in config['elements'] if e['name'] == 'oauth2'][0]
        oauth2_element['value'] = credentials.to_json()
        return config

    def tick(self, config):
        credentials = Credentials.new_from_json([e for e in config['elements'] if e['name'] == 'oauth2'][0]['value'])
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('analytics', 'v3', http=http)
        query_data = service.data().ga().get(
            ids = 'ga:' + [e for e in config['elements'] if e['name'] == 'account'][0]['value'],
            start_date = datetime.datetime.strptime([e for e in config['elements'] if e['name'] == 'start_date'][0]['value'], '%d/%m/%Y').strftime('%Y-%m-%d'),
            end_date = datetime.datetime.strptime([e for e in config['elements'] if e['name'] == 'end_date'][0]['value'], '%d/%m/%Y').strftime('%Y-%m-%d'),
            metrics = ','.join([e for e in config['elements'] if e['name'] == 'metrics'][0]['value']),
            dimensions = 'ga:date',
            sort = 'ga:date',
            max_results = '2000').execute()
        columns = query_data['columnHeaders']
        rows = query_data['rows']
        content_items = []
        for row in rows:
            configured_display_name = self.generate_configured_display_name(config)
            content_item = {
                'id':md5('%s-%s' % (config['id'], row[0])).hexdigest(),
                'text':[{'title':'%s Data for %s' % (configured_display_name, datetime.datetime.strptime(row[0], '%Y%m%d').strftime('%m/%d/%Y'))}],
                'time':int(calendar.timegm(datetime.datetime.strptime(row[0], '%Y%m%d').timetuple())),
                'channel':{
                    'id':md5(config['type'] + config['sub_type']).hexdigest(),
                    'type':config['type'],
                    'sub_type':config['sub_type']},
                'source':{
                    'id':config['id'],
                    'display_name':self.generate_configured_display_name(config)},
                'extensions':{}}
            for c in range(1, len(columns)):
                header = columns[c]
                value = row[c]
                if header['dataType'] in ['INTEGER']:
                    value = int(value)
                    value_type = 'float'
                elif header['dataType'] in ['FLOAT', 'CURRENCY', 'PERCENT']:
                    value = round(float(value), 2)
                    value_type = 'float'
                else:
                    value = str(value)
                    value_type = 'string'
                content_item['extensions'][header['name'].replace('ga:', '')] = {
                    'type':value_type,
                    'value': value
                }

            content_items.append(content_item)
        return content_items

