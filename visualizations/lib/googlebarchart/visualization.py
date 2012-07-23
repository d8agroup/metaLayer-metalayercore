from django.utils.html import escape
from utils import get_pretty_date
from metalayercore.visualizations.classes import VisualizationBase
from django.utils import simplejson as json

class Visualization(VisualizationBase):

    bar_limit = 5
    steps_backwards = 5

    def get_unconfigured_config(self):
        """
        Return the dict configuration needed to add the data point to the UI

        Returns
        -------
        dict: the configuration needed to use this data point
        """
        return {
            'name':'googlebarchart',
            'display_name_short':'Bar',
            'display_name_long':'Bar Chart',
            'image_small':'/static/images/thedashboard/bar_chart.png',
            'unconfigurable_message':'There is no category data available to be plotted. Try adding something like '
                                     'sentiment analysis',
            'instructions':'Bar charts provide a great way to visualize category based data. You can choose to visualize '
                           'the total value for these categories or break them down over time.',
            'filter_message':'Click a bar to filter the results above',
            'type':'javascript',
            'configured':False,
            'elements':[
                {
                    'name':'time',
                    'display_name':'Visualize over time?',
                    'help':'',
                    'type':'hidden',
                    'values':[
                        'No - Show totals only',
                        'Yes - Break down by time'
                    ],
                    'value':'No - Show totals only'
                },
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
                    'value':'Bar Chart'
                }
            ],
            'data_dimensions':[
                {
                    'name':'category1',
                    'display_name':'Bars',
                    'type':['string', 'float'],
                    'help':''
                }
            ]
        }

    def generate_search_query_data(self, config, search_configuration):
        return_data = []
        dimensions_of_type_string = [d for d in config['data_dimensions'] if d['value']['type'] == 'string']
        for dimension in dimensions_of_type_string:
            return_data.append([{
                'name':dimension['value']['value'],
                'type':'basic_facet',
                'limit':10
            }])
        return return_data or [{}]

    def render_javascript_based_visualization(self, config, search_results_collection, search_configuration):
        data_columns, data_rows = self._generate_data_without_time(config, search_results_collection, search_configuration)
        legend = False
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
            'colors':colors,
            'title':escape([e for e in config['elements'] if e['name'] == 'title'][0]['value']),
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
                'position':'right' if legend else 'none',
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

        data_dimension = config['data_dimensions'][0]['value']['value']
        js = "" \
            "$.getScript('https://www.google.com/jsapi', function(){ google.load('visualization', '1', {'packages': ['corechart'], 'callback':drawchart_VISUALIZATION_ID}); });\n" \
            "function drawchart_VISUALIZATION_ID() {\n" \
            "   if (!document.getElementById('v_VISUALIZATION_ID')) return;\n" \
            "   data_VISUALIZATION_ID = new google.visualization.DataTable();\n" \
            "   DATA_COLUMNS\n" \
            "   data_VISUALIZATION_ID.addRows(DATA_ROWS);\n" \
            "   var options = OPTIONS;\n" \
            "   chart_VISUALIZATION_ID = new google.visualization.BarChart(document.getElementById('v_VISUALIZATION_ID'));\n"\
            "   function select_handler_VISUALIZATION_ID(){\n"\
            "       var selected_item = chart_VISUALIZATION_ID.getSelection()[0];\n"\
            "       if (selected_item) {\n"\
            "            var data = { filter_name:'" + data_dimension + "', filter_value:data_VISUALIZATION_ID.getValue(selected_item.row, 0) }; \n"\
            "            $('#v_VISUALIZATION_ID').parents('.collection_container').dashboard_collection('apply_search_filter', data);\n"\
            "       }\n"\
            "   }\n"\
            "   google.visualization.events.addListener(chart_" + config['id'] + ", 'select', select_handler_" + config['id'] + ");\n"\
            "   chart_VISUALIZATION_ID.draw(data_VISUALIZATION_ID, options);\n" \
            "}"

        return js.replace('VISUALIZATION_ID', config['id'])\
            .replace('DATA_COLUMNS', data_columns)\
            .replace('DATA_ROWS', data_rows)\
            .replace('OPTIONS', options)

    def _generate_data_without_time(self, config, search_results_collection, search_configuration):
        search_result = search_results_collection[0]
        data_dimensions_value = config['data_dimensions'][0]['value']
        data_rows = []
        data_columns = [{'type':'string', 'name':data_dimensions_value['name']}, {'type':'number', 'name':'count'}]
        if data_dimensions_value['type'] == 'string':
            facets = [fg for fg in search_result['facet_groups'] if fg['name'] == data_dimensions_value['value']][0]['facets']
            data_rows = [[f['name'], f['count']] for f in facets]
        elif data_dimensions_value['type'] == 'float':
            stats = [search_result['stats'][stats_group] for stats_group in search_result['stats'].keys() if stats_group == data_dimensions_value['value']][0]
            data_rows.append(['Maximum', stats['max']])
            data_rows.append(['Minimum', stats['min']])
            data_rows.append(['Average', stats['mean']])
        return data_columns, data_rows

    def _generate_data_with_time(self, config, search_results_collection, search_configuration):
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
            if x >= len(search_results_collection):
                continue
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
        return data_columns, data_rows