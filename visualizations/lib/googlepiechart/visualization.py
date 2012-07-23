from django.utils.html import escape
from metalayercore.visualizations.classes import VisualizationBase
from django.utils import simplejson as json

class Visualization(VisualizationBase):

    def get_unconfigured_config(self):
        return {
            'name':'googlepiechart',
            'display_name_short':'Pie',
            'display_name_long':'Pie Chart',
            'image_small':'/static/images/lib/Impressions/pie_chart.png',
            'unconfigurable_message':'There is no category data available to be plotted. Try adding something like '
                                     'sentiment analysis',
            'instructions':'The pie chart is perhaps the most widely used chart in business and although some criticize '
                           'it, it remains a popular choice when you want to visualize proportions and where exact '
                           'comparison of values is not needed, and they can look really nice.',
            'filter_message':'Click a pie slice to filter the results above',
            'type':'javascript',
            'configured':False,
            'elements':[
                self._generate_colorscheme_config_element(),
                {
                    'name':'background',
                    'display_name':'Background Color',
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
                    'value':'Pie Chart'
                }
            ],
            'data_dimensions':[
                {
                    'name':'category1',
                    'display_name':'Pie Slices',
                    'type':['string'],
                    'help':''
                }
            ]
        }

    def generate_search_query_data(self, config, search_configuration):
        return_data = []
        for dimension in config['data_dimensions']:
            return_data.append([{
                'name':dimension['value']['value'],
                'type':'basic_facet',
                'limit':5
            }])
        return return_data

    def render_javascript_based_visualization(self, config, search_results_collection, search_configuration):
        data_dimension = config['data_dimensions'][0]['value']['value']
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
             "           chart_" + config['id'] + " = new google.visualization.PieChart(document.getElementById('v_" + config['id'] + "'));\n"\
             "           \n"\
             "           function select_handler_" + config['id'] + "(){\n"\
             "               var selected_item = chart_" + config['id'] + ".getSelection()[0];\n"\
             "               if (selected_item) {\n"\
             "                    var data = { filter_name:'" + data_dimension + "', filter_value:data_" + config['id'] + ".getValue(selected_item.row, 0) }; \n"\
             "                    $('#v_" + config['id'] + "').parents('.collection_container').dashboard_collection('apply_search_filter', data);\n"\
             "               }\n"\
             "           }\n"\
             "           google.visualization.events.addListener(chart_" + config['id'] + ", 'select', select_handler_" + config['id'] + ");\n"\
             "           chart_" + config['id'] + ".draw(data_" + config['id'] + ", options);\n"\
             "       }\n"\
             "   }\n"\
             ");\n"

        #TODO this only support one data dimension at the moment
        search_result = search_results_collection[0]
        data_dimensions_value = config['data_dimensions'][0]['value']
        facets = [fg for fg in search_result['facet_groups'] if fg['name'] == data_dimensions_value['value']][0]['facets']
        data_columns = [{'type':'string', 'name':data_dimensions_value['name']}, {'type':'number', 'name':'count'}]
        data_rows = [[f['name'], f['count']] for f in facets]
        data_columns = '\n'.join(["data_" + config['id'] + ".addColumn('%s', '%s');" % (t['type'], t['name']) for t in data_columns])
        number_of_data_rows = len(data_rows)
        data_rows = json.dumps(data_rows)

        background = [e for e in config['elements'] if e['name'] == 'background'][0]['value']
        if background == 'Dark':
            background_color = '#333333'
            text_color = '#FFFFFF'
        else:
            background_color = '#FFFFFF'
            text_color = '#000000'

        color_scheme = [e for e in config['elements'] if e['name'] == 'colorscheme'][0]['value']
        colors = self._generate_colors(color_scheme, number_of_data_rows)

        options = json.dumps({
            'backgroundColor':background_color,
            'title':escape([e for e in config['elements'] if e['name'] == 'title'][0]['value']),
            'titleTextStyle':{
                'color':text_color
            },
            'colors':colors,
            'legend':{
                'position':'right',
                'textStyle':{
                    'color':text_color
                }
            },
        })

        js = js.replace('{data_columns}', data_columns)
        js = js.replace('{data_rows}', data_rows)
        js = js.replace('{options}', options)
        return js