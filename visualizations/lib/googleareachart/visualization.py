from django.utils.html import escape
from utils import get_pretty_date
from metalayercore.visualizations.classes import VisualizationBase
from django.utils import simplejson as json

class Visualization(VisualizationBase):

    bar_limit = 5
    steps_backwards = 5

    def get_unconfigured_config(self):
        return {
            'name':'googleareachart',
            'display_name_short':'Area',
            'display_name_long':'Area chart',
            'image_small':'/static/images/thedashboard/area_chart.png',
            'unconfigurable_message':'There is no category data available to be plotted. Try adding something like '
                                     'sentiment analysis',
            'instructions':'Area charts make it really easy to contrast discrete category based data over time.',
            'type':'javascript',
            'configured':False,
            'elements':[
                self._generate_colorscheme_config_element(),
                {
                    'name':'background',
                    'display_name':'Background',
                    'help':'',
                    'type':'select',
                    'values':[
                        'Light',
                        'Dark'
                    ],
                    'value':'Light'
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
                {
                    'name':'category1',
                    'display_name':'Areas',
                    'type':'string',
                    'help':''
                }
            ]
        }

    def generate_search_query_data(self, config, search_configuration):
        return_data = []
        start_time, end_time = self._extract_time_bounds_from_search_configuration(search_configuration)
        time_interval = int((end_time - start_time) / self.steps_backwards)
        for s in range(start_time, end_time, time_interval):
            this_search = []
            for dimension in config['data_dimensions']:
                this_search.append({
                    'name':dimension['value']['value'],
                    'type':'basic_facet'
                })
            this_search.append({
                'name':'time',
                'range':{'start':s, 'end':(s + time_interval - 1)},
                'type':'range_query'
            })
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
             "           var data = new google.visualization.DataTable();\n"\
             "           {data_columns}\n"\
             "           data.addRows(\n"\
             "               {data_rows}\n"\
             "           );\n"\
             "           var options = {options};\n"\
             "           var chart = new google.visualization.AreaChart(document.getElementById('v_" + config['id'] + "'));\n"\
             "           chart.draw(data, options);\n"\
             "       }\n"\
             "   }\n"\
             ");\n"

        #TODO this only support one data dimension at the moment
        data_columns = [{'type':'string', 'name':'Time'}]
        data_rows = []
        data_dimensions_value = config['data_dimensions'][0]['value']

        start_time, end_time = self._extract_time_bounds_from_search_configuration(search_configuration)
        time_interval = int((end_time - start_time) / self.steps_backwards)

        array_of_start_times = range(start_time, end_time, time_interval)
        results_data_columns = []
        for search_result in search_results_collection:
            facets = [fg for fg in search_result['facet_groups'] if fg['name'] == data_dimensions_value['value']][0]['facets']
            for f in facets:
                if f['name'] not in results_data_columns:
                    results_data_columns.append(f['name'])
        data_columns += [{'type':'number', 'name':'%s' % c } for c in results_data_columns]
        number_of_empty_ranges = 0
        for x in range(len(array_of_start_times)):
            search_result = search_results_collection[x]
            start_time_pretty = get_pretty_date(array_of_start_times[x] + time_interval)
            data_row = [start_time_pretty]
            facets = [fg for fg in search_result['facet_groups'] if fg['name'] == data_dimensions_value['value']][0]['facets']
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
            data_rows.append(data_row)
        if number_of_empty_ranges == len(array_of_start_times):
            return "$('#" + config['id'] + "').html(\"<div class='empty_dataset'>Sorry, there is no data to visualize</div>\");"

        number_of_colors = len(data_columns) - 1
        data_columns = '\n'.join(["data.addColumn('%s', '%s');" % (t['type'], t['name']) for t in data_columns])
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
                'baselineColor':line_color,
                'textStyle':{
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
