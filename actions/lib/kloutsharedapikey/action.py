import httplib
import urllib
from logger import Logger
from django.utils import simplejson as json
from metalayercore.actions.classes import BaseAction
from metalayercore.actions.controllers import ActionController

class Action(BaseAction):

    api_limit = 20

    def get_unconfigured_config(self):
        return {
            'name':'kloutsharedapikey',
            'display_name_short':'Influence',
            'display_name_long':'Twitter Influence by Klout',
            'image_small':'/static/images/thedashboard/actions/klout_small.jpg',
            'instructions':'This actions does not need configuring.',
            'configured':True,
            'elements':[],
            'content_properties':{
                'added':[
                    {
                        'display_name':'Influence',
                        'name':'influence',
                        'type':'string'
                    },
                    {
                        'display_name':'Raw Influence',
                        'name':'raw_influence',
                        'type':'float'
                    },
                ]
            }
        }

    def run(self, config, content):
        content_from_twitter = [c for c in content if self._content_is_from_twitter(c)]
        return_values = [
            {
                'id':c['id'],
                'username':c['author_display_name'],
                'influence':self._get_cached_value(c['author_display_name'])['influence'],
                'raw_influence':self._get_cached_value(c['author_display_name'])['raw_influence']
            } for c in content_from_twitter]
        user_names = [x['username'] for x in return_values if not x['influence']]
        x = 0
        while x < len(user_names):
            self._call_api(user_names[x:x+self.api_limit], return_values)
            x += self.api_limit

        return [
            {
                'id':x['id'],
                'influence':x['influence'],
                'raw_influence':x['raw_influence']
            } for x in return_values]

    def get_content_item_template(self):
        config = self.get_unconfigured_config()
        controller = ActionController(config)
        influence_property = config['content_properties']['added'][0]
        encoded_property = controller._search_encode_property(influence_property)
        return ""\
               "{{if " + encoded_property + " && " + encoded_property + " != '_none'}}"\
               "    <li class='action_values influence'>"\
               "        <label><img src='" + config['image_small'] + "' style='position:relative;top:5px;left:-2px;width:16px;height:16px;'/>&nbsp;Influence:</label>&nbsp;"\
               "        <span style='font-weight:bold;'>"\
               "            <a class='action_inline_filter' data-facet_name='" + encoded_property + "' data-facet_value='${" + encoded_property + "}'>"\
               "                ${" + encoded_property + "}"\
               "            </a>"\
               "        </span>"\
               "    </li>"\
               "{{/if}}"

    def _call_api(self, user_names, return_values):
        query_data = {'users':','.join(user_names), 'key':'2qus3q26rfnz2gsefxb2czg4'}
        query_data = urllib.urlencode(query_data)
        url = 'http://api.klout.com/1/klout.json?%s' % query_data
        try:
            response = urllib.urlopen(url).read()
            response = json.loads(response)
        except httplib.HTTPException as err:
            if err.code == 403:
                Logger.Error('%s - kloutsharedapikeyaction - rate limit exceeded' % __name__)
            else:
                Logger.Error('%s - kloutsharedapikeyaction - error: %s' % (__name__, err.message))
            return []
        except Exception as err:
            Logger.Error('%s - kloutsharedapikeyaction - error: %s' % (__name__, err.message))
            return []

        for user in response['users']:
            for return_value in return_values:
                if user['twitter_screen_name'] == return_value['username']:
                    return_value['influence'] = self._map_influence(user['kscore'])
                    return_value['raw_influence'] = user['kscore']

    def _content_is_from_twitter(self, item):
        if 'channel_type' not in item:
            return False
        try:
            item['channel_type'].index('twitter')
            return True
        except ValueError:
            return False

    def _get_cached_value(self, username):
        return ActionController.CacheGet(username, {'influence':None, 'raw_influence':None})

    def _map_influence(self, raw_influence):
        if not raw_influence:
            return 'none'
        try:
            raw_influence = float(raw_influence)
        except ValueError:
            return 'none'
        if raw_influence < 30:
            return 'low'
        if raw_influence < 50:
            return 'medium'
        return 'high'

