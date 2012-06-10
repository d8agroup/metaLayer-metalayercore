import tablib
from metalayercore.outputs.classes import BaseOutput

class Output(BaseOutput):

    excluded_keys = [
        'pretty_date',
        'language',
        'scope',
        'channel_sub_type',
    ]

    def get_unconfigured_config(self):
        return {
            'name':'tablibexceloutput',
            'display_name_short':'Excel',
            'display_name_long':'Excel',
            'type':'url',
            'instructions':''
        }

    def generate_output(self, config, search_results):
        full_list_of_attributes = []
        for item in search_results['content_items']:
            keys = [k for k in item.keys() if k not in self.excluded_keys]
            for key in keys:
                if key not in full_list_of_attributes:
                    full_list_of_attributes.append(key)

        data = tablib.Dataset()
        for item in search_results['content_items']:
            data_row = []
            for key in full_list_of_attributes:
                value = item.get(key)
                data_row.append(self._split_value_if_needed(value) if value else None)
            data.append(data_row)

        data.headers = [self._map_header(key) for key in full_list_of_attributes]

        excel = data.xlsx
        return excel, 'application/ms-excel'

    def _split_value_if_needed(self, value):
        if type(value) == list:
            return '|'.join([v.replace('|', '') for v in value])
        return value

    def _map_header(self, key):
        if key.startswith('action'):
            key_parts = key.split('_')
            if len(key_parts) == 4:
                return key_parts[2]
        elif key.startswith('extension'):
            key_parts = key.split('_')
            if len(key_parts) == 3:
                return key_parts[1]
        elif key in ['date', 'time']:
            return '%s_utc' % key
        return key
