from random import shuffle
import time
import datetime

class VisualizationBase(object):
    color_schemes = {
        'Blue':[
            ['#3182BD'],
            ['#9ECAE1', '#3182BD'],
            ['#DEEBF7', '#9ECAE1', '#3182BD'],
            ['#EFF3FF', '#BDD7E7', '#6BAED6', '#2171B5'],
            ['#EFF3FF', '#BDD7E7', '#6BAED6', '#3182BD', '#08519C'],
        ],
        'Green':[
            ['#A1D99B'],
            ['#A1D99B', '#A1D99B'],
            ['#E5F5E0', '#A1D99B', '#A1D99B'],
            ['#EDF8E9', '#BAE4B3', '#74C476', '#238B45'],
            ['#EDF8E9', '#BAE4B3', '#74C476', '#31A354', '#006D2C']
        ],
        'Grey':[
            ['#636363'],
            ['#BDBDBD', '#636363'],
            ['#F0F0F0', '#BDBDBD', '#636363'],
            ['#F7F7F7', '#CCCCCC', '#969696', '#525252'],
            ['#F7F7F7', '#CCCCCC', '#969696', '#636363', '#252525']
        ],
        'Orange':[
            ['#E6550D'],
            ['#FDAE6B', '#E6550D'],
            ['#FEE6CE', '#FDAE6B', '#E6550D'],
            ['#FEEDDE', '#FDBE85', '#FD8D3C', '#D94701'],
            ['#FEEDDE', '#FDBE85', '#FD8D3C', '#E6550D', '#A63603']
        ],
        'Purple':[
            ['#756BB1'],
            ['#BCBDDC', '#756BB1'],
            ['#EFEDF5', '#BCBDDC', '#756BB1'],
            ['#F2F0F7', '#CBC9E2', '#9E9AC8', '#6A51A3'],
            ['#F2F0F7', '#CBC9E2', '#9E9AC8', '#756BB1', '#54278F']
        ],
        'Red':[
            ['#DE2D26'],
            ['#FC9272', '#DE2D26'],
            ['#FEE0D2', '#FC9272', '#DE2D26'],
            ['#FEE5D9', '#FCAE91', '#FB6A4A', '#CB181D'],
            ['#FEE5D9', '#FCAE91', '#FB6A4A', '#DE2D26', '#A50F15']
        ],
        'Blue - Green':[
            ['#2CA25F'],
            ['#99D8C9', '#2CA25F'],
            ['#E5F5F9', '#99D8C9', '#2CA25F'],
            ['#EDF8FB', '#B2E2E2', '#66C2A4', '#238B45'],
            ['#EDF8FB', '#B2E2E2', '#66C2A4', '#2CA25F', '#006D2C']
        ],
        'Blue - Purple':[
            ['#8856A7'],
            ['#9EBCDA', '#8856A7'],
            ['#E0ECF4', '#9EBCDA', '#8856A7'],
            ['#EDF8FB', '#B3CDE3', '#8C96C6', '#88419D'],
            ['#EDF8FB', '#B3CDE3', '#8C96C6', '#8856A7', '#810F7C']
        ],
        'Green - Blue':[
            ['#43A2CA'],
            ['#A8DDB5', '#43A2CA'],
            ['#E0F3DB', '#A8DDB5', '#43A2CA'],
            ['#F0F9E8', '#BAE4BC', '#7BCCC4', '#2B8CBE'],
            ['#F0F9E8', '#BAE4BC', '#7BCCC4', '#43A2CA', '#0868AC']
        ],
        'Orange - Red':[
            ['#E34A33'],
            ['#FDBB84', '#E34A33'],
            ['#FEE8C8', '#FDBB84', '#E34A33'],
            ['#FEF0D9', '#FDCC8A', '#FC8D59', '#D7301F'],
            ['#FEF0D9', '#FDCC8A', '#FC8D59', '#E34A33', '#B30000']
        ],
        'Purple - Red':[
            ['#DD1C77'],
            ['#C994C7', '#DD1C77'],
            ['#E7E1EF', '#C994C7', '#DD1C77'],
            ['#F1EEF6', '#D7B5D8', '#DF65B0', '#CE1256'],
            ['#F1EEF6', '#D7B5D8', '#DF65B0', '#DD1C77', '#980043']
        ],
        'Yellow - Brown':[
            ['#D95F0E'],
            ['#FEC44F', '#D95F0E'],
            ['#FFF7BC', '#FEC44F', '#D95F0E'],
            ['#FFFFD4', '#FED98E', '#FE9929', '#CC4C02'],
            ['#FFFFD4', '#FED98E', '#FE9929', '#D95F0E', '#993404']
        ]
    }

    def visualization_removed(self):
        pass

    def generate_search_query_data(self, config, search_configuration):
        data_queries = [
            {'name':dd['value']['value'], 'type':'basic_facet'} for dd in config['data_dimensions'] if dd['value']
        ]
        return [data_queries]

    def _parse_time_parameters(self, time_increment, steps_backwards, search_time_parameter):
        if time_increment == 'minutes':
            time_increment = 60 * 10 #ten minutes
        elif time_increment == 'hours':
            time_increment = 60 * 60 * 2 #two hours
        elif time_increment == 'days':
            time_increment = 60 * 60 * 24 #one day

        search_end_time = search_time_parameter.split('%20TO%20')[1].strip(']')
        end = int(time.time()) if search_end_time == '*' else int(search_end_time)
        start = end - (steps_backwards * time_increment)
        search_start_time = search_time_parameter.split('%20TO%20')[0].strip('[')
        if search_start_time != '*' and int(search_start_time) > start:
            start = int(search_start_time)
        return end, start, time_increment

    def _extract_time_bounds_from_search_configuration(self, search_configuration):
        search_end_time = search_configuration['search_filters']['time'].split('%20TO%20')[1].strip(']')
        if search_end_time == "*":
            search_end_time = int(time.time())
        else:
            search_end_time = int(search_end_time)
        search_start_time = search_configuration['search_filters']['time'].split('%20TO%20')[0].strip('[')
        try:
            search_start_time = int(search_start_time)
        except ValueError:
            search_start_time = datetime.datetime.now() - datetime.timedelta(days=30)
            search_start_time = time.mktime(search_start_time.timetuple())
        return search_start_time, search_end_time

    def _generate_colorscheme_config_element(self):
        colors = ['Blue', 'Green', 'Grey', 'Orange', 'Purple', 'Red' 'Blue - Green', 'Blue - Purple', 'Green - Blue', 'Orange - Red', 'Purple - Red', 'Yellow - Brown']
        shuffle(colors)
        return {
            'name':'colorscheme',
            'display_name':'Color Scheme',
            'help':'',
            'type':'select',
            'values': colors,
            'value':colors[0]
        }

    def _generate_colors(self, color_scheme, color_count):
        color_group = self.color_schemes[color_scheme] if color_scheme in self.color_schemes.keys() else self.color_schemes['Blue - Green']
        if color_count > len(color_group):
            color_count = len(color_group)
        return color_group[color_count - 1]

