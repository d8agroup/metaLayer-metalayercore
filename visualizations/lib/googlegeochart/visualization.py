from metalayercore.visualizations.classes import VisualizationBase
from django.utils import simplejson as json

class Visualization(VisualizationBase):
    def get_unconfigured_config(self):
        return {
            'name':'googlegeochart',
            'display_name_short':'Map',
            'display_name_long':'Map',
            'image_small':'/static/images/thedashboard/map.png',
            'unconfigurable_message':'There is no location data available, try adding a location detections action.',
            'instructions':'Maps provide a beautiful way to visualize location based data. You can configure this map '
                           'to focus on a continent and can choose between Country (Regions) or Marker type display.',
            'type':'javascript',
            'configured':False,
            'elements':[
                {
                    'name':'map_mode',
                    'display_name':'Map type',
                    'help':'Region works best with country data while Marker works well with cities or other places',
                    'type':'select',
                    'values':[
                        'Regions',
                        'Markers'
                    ],
                    'value':'Regions'
                },
                {
                    'name':'focus',
                    'display_name':'Map focus',
                    'help':'Choose a geographic region to focus the map on',
                    'type':'select',
                    'values':[
                        'World',
                        'North America',
                        'Europe',
                        'Asia',
                        'Africa',
                        'Americas',
                        'Oceania'
                    ],
                    'value':'World'
                },
                self._generate_colorscheme_config_element(),
                {
                    'name':'background',
                    'display_name':'Background',
                    'help':'',
                    'type':'select',
                    'values':[
                        'Light',
                        'Dark',
                    ],
                    'value':'Light'
                }
            ],
            'data_dimensions':[
                {
                    'name':'locations',
                    'display_name':'Location',
                    'type':'location_string',
                    'help':''
                }
            ]
        }

    def generate_search_query_data(self, config, search_configuration):
        data_queries = [
            {'name':dd['value']['value'], 'type':'basic_facet', 'limit':15} for dd in config['data_dimensions'] if dd['value']
        ]
        return [data_queries]

    def render_javascript_based_visualization(self, config, search_results_collection, search_configuration):
        search_results = search_results_collection[0]
        facets = [f['facets'] for f in search_results['facet_groups'] if f['name'] == config['data_dimensions'][0]['value']['value']][0]
        js = "" \
            "$.getScript\n" \
            "(\n" \
            "   'https://www.google.com/jsapi',\n" \
            "   function()" \
            "   {\n" \
            "       google.load('visualization', '1', {'packages': ['geochart'], 'callback':drawRegionsMap_" + config['id'] + "});\n" \
            "       function drawRegionsMap_" + config['id'] + "()\n" \
            "       {\n" \
            "           if(!document.getElementById('v_" + config['id'] + "'))\n" \
            "               return;\n" \
            "           var data = new google.visualization.DataTable();\n" \
            "           data.addColumn('string', 'Country');\n" \
            "           data.addColumn('number', 'Mentions');\n" \
            "           data.addRows([\n" \
            "               {data_rows}\n" \
            "           ]);\n" \
            "           var options = {options};\n" \
            "           var chart = new google.visualization.GeoChart(document.getElementById('v_" + config['id'] + "'));\n" \
            "           chart.draw(data, options);\n" \
            "       }\n" \
            "   }\n" \
            ");\n"

        data_rows = ','.join(["['%s', %i]" % (f['name'].replace('\'', ''), f['count']) for f in facets])
        js = js.replace("{data_rows}", data_rows)

        background = [e for e in config['elements'] if e['name'] == 'background'][0]['value']
        if background == 'Dark':
            background_color = '#333333'
            empty_region_color = '#CCCCCC'
        else:
            background_color = '#FFFFFF'
            empty_region_color = '#CCCCCC'

        color_scheme = [e for e in config['elements'] if e['name'] == 'colorscheme'][0]['value']
        colors = self._generate_colors(color_scheme, 200)
        colors = [colors[0], colors[-1]]

        options = {
            'backgroundColor':background_color,
            'datalessRegionColor':empty_region_color,
            'colorAxis':{
                'minValue':0,
                'colors':colors
            },
            'region':self._map_map_focus([e for e in config['elements']][1]['value'])
        }
        if [e for e in config['elements']][0]['value'] == 'Markers':
            options['displayMode'] = 'markers'
        options = json.dumps(options)
        js = js.replace('{options}', options)
        return js

    def _map_map_focus(self, focus):
        if focus == 'Africa': return '002'
        if focus == 'Europe': return '150'
        if focus == 'Americas': return '019'
        if focus == 'North America': return '021'
        if focus == 'Asia': return '142'
        if focus == 'Oceania': return '009'
        return 'world'
