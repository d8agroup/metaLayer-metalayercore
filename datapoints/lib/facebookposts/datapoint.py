import os
import time
import dateutil.tz
import dateutil.parser
from hashlib import md5

import facepy
from logger import Logger
from oauth2client.client import OAuth2WebServerFlow, Credentials
from metalayercore.datapoints.classes import BaseDataPoint
from metalayercore.oauth2bridge.controllers import FacebookOauth2Controller


class DataPoint(BaseDataPoint):
    flow = OAuth2WebServerFlow(
        client_id="THIS IS MANAGED ELSEWHERE",
        client_secret="THIS IS MANAGED ELSEWHERE",
        scope="manage_pages, read_insights",
        redirect_uri="THIS IS MANAGED ELSEWHERE",
        auth_uri="https://www.facebook.com/dialog/oauth",
        token_uri="https://graph.facebook.com/oauth/access_token")

    def get_unconfigured_config(self):
        """Return basic configuration for this datapoint. The meta_data
        attributes map directly to the Insights attributes from the FB API.
        Only Insights that return a single value are currently supported. For
        instance, `post_story_adds_by_action_type` is not supported because
        it returns multiple values: [{'value': {'like': 2}}]. The supported
        Insights have a single return value: [{'value': 2}].
        """

        return {
            'type':'facebookposts',
            'sub_type':'facebookposts',
            'is_live':False,
            'display_name_short':'Facebook Posts',
            'full_display_name':'Facebook Posts',
            'instructions':'Use this data to retrieve information about Facebook Posts.',
            'image_large':'/static/images/thedashboard/data_points/facebook_large.png',
            'image_medium':'/static/images/thedashboard/data_points/facebook_medium.png',
            'image_small':'/static/images/thedashboard/data_points/facebook_small.png',
            'configured':False,
            'elements': [
                {
                    'name':'oauth2',
                    'display_name':'oauth2',
                    'help':"""To access data from Facebook, you need to authorize Delv to collect data on your
                              behalf.<br/><br/>
                              Please click the Authorize button below, you will then be take to a Google web page so you can
                              authorize Delv.""",
                    'type':'oauth2',
                    'value':''
                },{
                    'name':'account',
                    'display_name':'Collect metrics from',
                    'help':'The Facebook Page to get data from.',
                    'type':'select',
                    'value':'',
                    'values':[]
                },
                self._generate_base_search_start_time_config_element(),
                self._generate_base_search_end_time_config_element(),
            ],
            'meta_data': [
                {
                    'display_name': 'Lifetime Post Total Reach',
                    'name': 'extensions_post_impressions_unique_f',
                    'type': 'float'
                },{
                    'display_name': 'Lifetime Post Total Impressions',
                    'name': 'extensions_post_impressions_f',
                    'type': 'float'
                },{
                    'display_name': 'Lifetime Post Organic Reach',
                    'name': 'extensions_post_impressions_organic_unique_f',
                    'type': 'float'
                },{
                    'display_name': 'Lifetime Post Organic Impressions',
                    'name': 'extensions_post_impressions_organic_f',
                    'type': 'float'
                },{
                    'display_name': 'Lifetime Post Reach by people who like your Page',
                    'name': 'extensions_post_impressions_fan_unique_f',
                    'type': 'float'
                },{
                    'display_name': 'Lifetime Post Impressions by people who have liked your Page',
                    'name': 'extensions_post_impressions_fan_f',
                    'type': 'float'
                },{
                    'display_name': 'Lifetime Engaged Users',
                    'name': 'extensions_post_engaged_users_f',
                    'type': 'float'
                },{
                    'display_name': 'Lifetime Post Consumers (Total Count)', # These are clicks
                    'name': 'extensions_post_consumptions_f',
                    'type': 'float'
                },{
                    'display_name': 'Lifetime Post Consumers (Unique Users)', # These are clicks
                    'name': 'extensions_post_consumptions_unique_f',
                    'type': 'float'
                },{
                    'display_name': 'Lifetime Negative Feedback from Users',
                    'name': 'extensions_post_negative_feedback_f',
                    'type': 'float'
                },{
                    'display_name': 'Lifetime Negative Feedback Users',
                    'name': 'extensions_post_negative_feedback_unique_f',
                    'type': 'float'
                },{
                    'display_name': 'Lifetime Talking About This (Post)',
                    'name': 'extensions_post_story_adds_unique_f',
                    'type': 'float'
                },{
                    'display_name': 'Lifetime Post Stories',
                    'name': 'extensions_post_story_adds_f',
                    'type': 'float'
                },{
                    'display_name': 'Lifetime Talking About This (Post)',
                    'name': 'extensions_post_storytellers_f',
                    'type': 'float'
                },{
                    'display_name': 'Lifetime Post Stories',
                    'name': 'extensions_post_stories_f',
                    'type': 'float'
                },
            ],
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
        """Generate a GUID for this datapoint/account combination."""

        account_id = [e for e in config['elements'] if e['name'] == 'account'][0]['value']
        return md5('%s %s' % (config['type'], account_id)).hexdigest()

    def generate_configured_display_name(self, config):
        """Generate a user-friendly name for this Insight, in this case
        'Facebook Posts: <ACCOUNT_NAME>'
        """

        account = [e for e in config['elements'] if e['name'] == 'account'][0]['values'][0]['name']
        return '%s: %s' % (config['display_name_short'], account)

    def validate_config(self, config):
        """Validate that the provided config is acceptable."""

        return True, {}

    def update_data_point_with_oauth_dependant_config(self, config):
        """Query the "accounts" endpoint to determine the list of "pages" the
        user has access to. This endpoint will also return Applications owned
        by the user so we explicitly exclude them from the list.
        """
        ignore_categories = ("Application",)

        credentials = Credentials.new_from_json([e for e in config['elements'] if e['name'] == 'oauth2'][0]['value'])
        facebook = facepy.GraphAPI(credentials.access_token)
        accounts = facebook.get('/me/accounts')['data']

        post_oauth_request_accounts = [{'value': _['id'], 'name': _['name']}
            for _ in accounts if _['category'] not in ignore_categories]
        accounts_element = [e for e in config['elements'] if e['name'] == 'account'][0]
        accounts_element['values'] = post_oauth_request_accounts
        oauth2_element = [e for e in config['elements'] if e['name'] == 'oauth2'][0]
        oauth2_element['value'] = credentials.to_json()

        return config

    def oauth_get_oauth2_return_handler(self, data_point_id):
        """Return the flow object after updating its current state."""

        flow = self.flow
        flow.params['state'] = '_'.join([data_point_id, self.get_unconfigured_config()['type']])
        return flow

    def oauth_credentials_are_valid(self, credentials_json):
        """Ensure the OAuth credentials are valid."""

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
        """Determine if access has been granted (OAuth authorization)."""

        credentials = FacebookOauth2Controller.PollForNewCredentials(self.oauth_get_oauth2_return_handler(config['id']))
        if not credentials:
            return None
        oauth_element = [e for e in config['elements'] if e['name'] == 'oauth2'][0]
        oauth_element['value'] = credentials.to_json()
        return config

    def oauth_get_oauth_authenticate_url(self, id):
        """Return the OAuth2.0 authorization URL."""

        authorize_url = FacebookOauth2Controller.GetOauth2AuthorizationUrl(self.oauth_get_oauth2_return_handler(id))
        return authorize_url

    def tick(self, config):
        """Query the FB API and grab the latest N posts with Insights."""

        Logger.Info('%s - tick - started - with config: %s' % (__name__, config))
        credentials = Credentials.new_from_json([e for e in config['elements'] if e['name'] == 'oauth2'][0]['value'])
        account_id = [e for e in config['elements'] if e['name'] == 'account'][0]['value']

        # Fetch 25 most recent posts and build up list of Graph API requests
        # for batch querying of Insights data.
        limit = 25
        facebook = facepy.GraphAPI(credentials.access_token)
        posts = facebook.get('/%s/posts?limit=%d' % (account_id, limit))['data']
        requests = [{'method': 'GET', 'relative_url': '/%s/insights' % _['id']} for _ in posts]

        insights = {}
        # Fetch Insights information for each post
        for insight in facebook.batch(requests):
            post_id = insight['data'][0]['id'].split('/')[0]
            insights[post_id] = insight['data']

        content_items = self._generate_content_items(posts, insights, config)
        Logger.Debug('%s - tick - finished' % __name__)
        return content_items

    def _generate_content_items(self, posts, insights, config):
        """Munge the Facebook posts into our standard format.
        `posts` is a list of dictionaries from the /posts API endpoint.
        `insights` is a dictionary of results from the /insights API endpoint,
        keyed by the post ID.
        """

        content_items = []
        guid = self.generate_configured_guid(config)
        display_name = self.generate_configured_display_name(config)

        # These are the extensions we will index as per the meta_data list
        # above. The `name` value is munged to jive with the FB API.
        attrs = ['_'.join(_['name'].split('_')[1:-1]) for _ in config['meta_data']]

        for post in posts:
            # Generate the basic content item template
            item = {
                'id': post['id'],
                'time': int(time.mktime(dateutil.parser.parse(post['created_time']).astimezone(dateutil.tz.tzutc()).timetuple())),
                'link': post['actions'][0]['link'],
                'text': [{'title': post['message']}],
                'author': {
                    'display_name': post['from']['name'],
                    'link': 'http://www.facebook.com/%s' % post['from']['id'],
                    'image': post['icon'],
                },
                'channel': {
                    'id': md5(config['type'] + config['sub_type']).hexdigest(),
                    'type': config['type'],
                    'sub_type': config['sub_type']
                },
                'source': {
                    'id': guid,
                    'display_name': display_name,
                },
                'extensions': {}
            }

            # Attach all the insight information
            item['extensions'] = \
                dict((_['name'], dict(type='float', value=_['values'][0]['value'])) for _ in insights[post['id']] if _['name'] in attrs)

            content_items.append(item)

        return content_items
