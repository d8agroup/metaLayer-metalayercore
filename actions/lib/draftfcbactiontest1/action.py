from metalayercore.actions.classes import BaseAction
from metalayercore.actions.controllers import ActionController

class Action(BaseAction):
    def get_unconfigured_config(self):
        return {
            'name':'draftfcbactiontest1',
            'display_name_short':'Draft FCB Data',
            'display_name_long':'Draft FCB Embedded Data',
            'image_small':'http://a0.twimg.com/profile_images/1865030972/Draftfcb-Logo-Small-V2_normal.jpg',
            'instructions':'This actions does not need configuring.',
            'configured':True,
            'elements':[],
            'content_properties':{
                'added':[
                    {
                        'display_name':'Followers',
                        'name':'followers',
                        'type':'string'
                    },
                    {
                        'display_name':'Draft FCB Sentiment',
                        'name':'draftfcbsentiment',
                        'type':'string'
                    },
                ]
            }
        }

    def run(self, config, content):
        return [{'id':i['id'], 'followers':self._map_followers(i), 'draftfcbsentiment':self._map_draftfcb_sentiment(i)} for i in content]
        pass

    def get_content_item_template(self):
        config = self.get_unconfigured_config()
        controller = ActionController(config)
        followers = config['content_properties']['added'][0]
        sentiment = config['content_properties']['added'][1]
        return ""\
            "{{if " + controller._search_encode_property(followers) + "}}"\
            "    <li class='action_values'>"\
            "        <label><img src='http://a0.twimg.com/profile_images/1865030972/Draftfcb-Logo-Small-V2_normal.jpg' style='position:relative;top:5px;left:-2px;width:16px;height:16px;'/>&nbsp;Followers:</label>&nbsp;"\
            "        <span style='font-weight:bold;'>${" + controller._search_encode_property(followers) + "}</span>"\
            "    </li>"\
            "{{/if}}" \
            "{{if " + controller._search_encode_property(sentiment) + "}}"\
            "    <li class='action_values'>"\
            "        <label><img src='http://a0.twimg.com/profile_images/1865030972/Draftfcb-Logo-Small-V2_normal.jpg' style='position:relative;top:5px;left:-2px;width:16px;height:16px;'/>&nbsp;Draft FCB Sentiment:</label>&nbsp;"\
            "        <span style='font-weight:bold;'>${" + controller._search_encode_property(sentiment) + "}</span>"\
            "    </li>"\
            "{{/if}}" \
            ""

    def _map_followers(self, content_item):
        if 'extensions_followers_f' not in content_item:
            return 'none'
        try:
            followers = float(content_item['extensions_followers_f'])
        except ValueError:
            return 'none'
        if followers < 100:
            return 'low (1 to 100)'
        if followers < 500:
            return 'mid (100 to 500)'
        return 'high (over 500)'

    def _map_draftfcb_sentiment(self, content_item):
        if 'extensions_draftfcbsentiment_s' not in content_item:
            return 'none'
        sentiment = content_item['extensions_draftfcbsentiment_s']
        if 'pos' in sentiment:
            return 'positive'
        if 'neg' in sentiment:
            return 'negative'
        return 'neutral'
