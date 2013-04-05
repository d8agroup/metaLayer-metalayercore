import datetime
from django.utils.html import escape
from metalayercore.visualizations.classes import VisualizationBase
from django.utils import simplejson as json
from utils import get_pretty_date


class Visualization(VisualizationBase):

    bar_limit = 5
    steps_backwards = 5

    def get_unconfigured_config(self):
        return {
            'name':'googlecolumnchart',
            'display_name_short':'Column',
            'display_name_long':'Column chart',
            'image_small':'/static/images/thedashboard/area_chart.png',
            'unconfigurable_message':'There is no data graph',
            'instructions':"""
                Column charts can be used to graph one or more metric over another.</b>
                """,
            'filter_message':'This type of chart does not support filtering',
            'type':'javascript',
            'configured':False,
            'number_of_required_dimensions':2,
            'elements':[
                self._generate_colorscheme_config_element(),
                {
                    'name':'background',
                    'display_name':'Background',
                    'help':'',
                    'type':'select',
                    'values':[
                        'Dark',
                        'Light'
                    ],
                    'value':'Dark'
                },
                {
                    'name':'title',
                    'display_name':'Chart Title',
                    'help':'',
                    'type':'text',
                    'value':'Area Chart'
                }
            ],
            'data_dimensions':[
                { 'name':'xaxis', 'display_name':'Graph Over', 'type':['string', 'float'], 'help':'' },
                { 'name':'category2', 'display_name':'Metric 2', 'type':['string', 'float'], 'help':'' },
                { 'name':'category3', 'display_name':'Metric 3', 'type':['string', 'float'], 'help':'' },
            ]
        }

    def generate_search_query_data(self, config, search_configuration):
        return_data = []

        xaxis_dimension = [d for d in config['data_dimensions'] if d['name'] == 'xaxis'][0]
        xaxis_metric = xaxis_dimension['value']['value']
        
        if xaxis_dimension['value']['type'] == 'string':
            category2_metric = [d for d in config['data_dimensions'] if d['name'] == 'category2'][0]['value']['value']
            return_data.append([{
                'type': 'pivot_query',
                'pivot': xaxis_metric + "," + category2_metric
            }])
        else:        
            max_and_min = search_configuration['base_search_configuration']['facet_range_groups'][xaxis_metric]
            interval = int((max_and_min['max'] - max_and_min['min']) / self.steps_backwards)
            for s in range(max_and_min['min'], max_and_min['max'], interval):
                this_search = []
                for dimension in config['data_dimensions']:
                    if dimension['value']['type'] == 'string':
                        this_search.append({
                            'name':dimension['value']['value'],
                            'type':'basic_facet'
                        })
                range_query = {'name': xaxis_metric, 'range': {'start': s, 'end': (s + interval - 1)}, 'type': 'range_query'}
                this_search.append(range_query)
                return_data.append(this_search)

        return return_data

    def render_javascript_based_visualization(self, config, search_results_collection, search_configuration):
        js = ""\
             "$.getScript\n"\
             "(\n"\
             "   'https://www.google.com/jsapi',\n"\
             "   function()"\
             "   {\n"\
             "       google.load('visualization', '1', {'packages': ['corechart'], 'callback':drawchart_" + config['id'] + "});\n"\
             "       function drawchart_" + config['id'] + "()\n"\
             "       {\n"\
             "           if(!document.getElementById('v_" + config['id'] + "'))\n"\
             "               return;\n"\
             "           data_" + config['id'] + " = new google.visualization.DataTable();\n"\
             "           {data_columns}\n"\
             "           data_" + config['id'] + ".addRows(\n"\
             "               {data_rows}\n"\
             "           );\n"\
             "           var options = {options};\n"\
             "           chart_" + config['id'] + " = new google.visualization.ColumnChart(document.getElementById('v_" + config['id'] + "'));\n"\
             "           chart_" + config['id'] + ".draw(data_" + config['id'] + ", options);\n"\
             "       }\n"\
             "   }\n"\
             ");\n"

        data_rows = []

        xaxis_dimension = [d for d in config['data_dimensions'] if d['name'] == 'xaxis'][0]

        if xaxis_dimension['value']['type'] == 'string':
            pass
        else:

            data_columns= [{'type':'string', 'name':xaxis_dimension['name']}]
            max_and_min = search_configuration['base_search_configuration']['facet_range_groups'][xaxis_dimension['value']['value']]
            interval = int((max_and_min['max'] - max_and_min['min']) / self.steps_backwards)
            array_of_intervals = range(max_and_min['min'], max_and_min['max'], interval)

            data_dimensions = [d for d in config['data_dimensions'] if d['name'] != 'xaxis' and d['value']['value']]

            results_data_columns = []
            for data_dimension_value in [d['value'] for d in data_dimensions]:
                if data_dimension_value['type'] != 'string':
                    results_data_columns.append(data_dimension_value['name'])
                else:
                    for search_result in search_results_collection:
                        facets = [fg for fg in search_result['facet_groups'] if fg['name'] == data_dimension_value['value']][0]['facets']
                        for f in facets:
                            if f['name'] not in results_data_columns:
                                results_data_columns.append(f['name'])

            data_columns += [{'type':'number', 'name':'%s' % c } for c in results_data_columns]
            number_of_empty_ranges = 0
            for x in range(len(array_of_intervals)):
                if x >= len(search_results_collection):
                    continue
                search_result = search_results_collection[x]

                label = '%i to %i' % (array_of_intervals[x], (array_of_intervals[x] + interval))
                data_row = [label]

                for data_dimension_value in [d['value'] for d in data_dimensions]:
                    if data_dimension_value['type'] == 'string':
                        facets = [fg for fg in search_result['facet_groups'] if fg['name'] == data_dimension_value['value']][0]['facets']
                        dynamic_data_rows = []
                        for c in results_data_columns:
                            candidate_facet = [f for f in facets if f['name'] == c]
                            if candidate_facet:
                                dynamic_data_rows.append(candidate_facet[0]['count'])
                            else:
                                dynamic_data_rows.append(0)
                        if not sum(dynamic_data_rows):
                            number_of_empty_ranges += 1
                        data_row += dynamic_data_rows
                    else:
                        if data_dimension_value['value'] in search_result['stats'] and search_result['stats'][data_dimension_value['value']]:
                            data_row.append(search_result['stats'][data_dimension_value['value']]['sum'])
                        else:
                            data_row.append(0)
                data_rows.append(data_row)

            if number_of_empty_ranges == len(array_of_intervals):
                return "$('#" + config['id'] + "').html(\"<div class='empty_dataset'>Sorry, there is no data to visualize</div>\");"

        number_of_colors = len(data_columns) - 1
        data_columns = '\n'.join(["data_%s.addColumn('%s', '%s');" % (config['id'], t['type'], t['name']) for t in data_columns])
        data_rows = json.dumps(data_rows)

        color_scheme = [e for e in config['elements'] if e['name'] == 'colorscheme'][0]['value']
        colors = self._generate_colors(color_scheme, number_of_colors)

        background = [e for e in config['elements'] if e['name'] == 'background'][0]['value']
        if background == 'Dark':
            background_color = '#333333'
            text_color = '#FFFFFF'
            line_color = '#DDDDDD'
        else:
            background_color = '#FFFFFF'
            text_color = '#000000'
            line_color = '#333333'

        options = json.dumps({
            'backgroundColor':background_color,
            'title':escape([e for e in config['elements'] if e['name'] == 'title'][0]['value']),
            'colors':colors,
            'titleTextStyle':{
                'color':text_color
            },
            'hAxis':{
                'title':xaxis_dimension['value']['name'],
                'baselineColor':line_color,
                'textStyle':{
                    'color':text_color
                },
                'titleTextStyle':{
                    'color':text_color
                },
                'slantedText':True,
                'gridlines.color':line_color,
                },
            'legend':{
                'position':'right',
                'textStyle':{
                    'color':text_color
                }
            },
            'vAxis':{
                'baselineColor':line_color,
                'textStyle':{
                    'color':text_color
                },
                'minValue':0
            }
        })

        js = js.replace('{data_columns}', data_columns)
        js = js.replace('{data_rows}', data_rows)
        js = js.replace('{options}', options)
        return js

    def _days_between_start_and_end_time(self, start_time, end_time):
        return (end_time - start_time) / 86400

    def _get_pretty_date(self, time_value, days_in_time_range):
        if days_in_time_range:
            formatted_time = (datetime.date.fromtimestamp(time_value) + datetime.timedelta(1)).strftime('%m/%d/%y')
        else:
            formatted_time = get_pretty_date(time_value)
        return formatted_time