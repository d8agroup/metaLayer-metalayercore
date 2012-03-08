from django.utils import simplejson as json
from metalayercore.outputs.classes import BaseOutput
from datetime import datetime

class Output(BaseOutput):
    def get_unconfigured_config(self):
        return {
            'name':'jsonoutput',
            'display_name_short':'JSON',
            'display_name_long':'JSON',
            'type':'url',
            'instructions':''
        }

    def generate_output(self, config, search_results):
        json_return = {
            'service':'metaLayer - dashboard',
            'date':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'items':search_results['content_items']
        }
        json_return = json.dumps(json_return)
        return json_return, 'application/json'