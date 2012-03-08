from metalayercore.visualizations.classes import VisualizationBase
from django.utils import simplejson as json

class Visualization(VisualizationBase):

    def get_unconfigured_config(self):
        return {
            'name':'d3cloud',
            'display_name_short':'Words',
            'display_name_long':'Words',
            'image_small':'/static/images/thedashboard/area_chart.png',
            'unconfigurable_message':'There is no category data available to be plotted. Try adding something like tagging',
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
                    'name':'style',
                    'display_name':'Style',
                    'help':'',
                    'type':'select',
                    'values':[
                        'Standard',
                        'Word Mashup'
                    ],
                    'value':'Standard'
                },
                {
                    'name':'wordlimit',
                    'display_name':'Word Limit',
                    'help':'',
                    'type':'select',
                    'values':[
                        '100',
                        '50',
                        '20',
                        '10',
                        '5'
                    ],
                    'value':'100'
                }
            ],
            'data_dimensions':[
                    {
                    'name':'category1',
                    'display_name':'Words',
                    'type':'string',
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
                'limit':int([e for e in config['elements'] if e['name'] == 'wordlimit'][0]['value'])
            }])
        return return_data

    def render_javascript_based_visualization(self, config, search_results_collection, search_configuration):
        js = ''\
        'function font_size(d) {\n' \
        '    var words = WORDS;'\
        '    var scale = (d.size / words[0].size);\n'\
        '    if (!MASHUP) {' \
        '        if (scale < 0.2) scale = 0.2;\n'\
        '        if (scale > 0.8) scale = 0.8;' \
        '    }\n'\
        '    var size = Math.round(scale * Math.round($("#v_VISUALIZATION_ID").width()/8));\n'\
        '    return size;\n'\
        '}\n'\
        'function draw(words) {\n'\
        '    d3.select("#v_VISUALIZATION_ID").append("svg")\n'\
        '    .attr("width", $("#v_VISUALIZATION_ID").width())\n'\
        '    .attr("height", $("#v_VISUALIZATION_ID").height())\n'\
        '    .style("background-color", "BACKGROUND_COLOR")\n'\
        '    .append("g")\n'\
        '   .attr("transform", "translate(" + Math.round($("#v_VISUALIZATION_ID").width() / 2) + "," + ($("#v_VISUALIZATION_ID").height() / 2) + ")")\n'\
        '    .selectAll("text")\n'\
        '    .data(words)\n'\
        '    .enter().append("text")\n'\
        '    .style("font-size", function(d) {\n ' \
        '       if (MASHUP) return font_size(d) + "px";\n' \
        '       return d.size + "px";' \
        '    })\n'\
        '    .style("fill", function(d) {\n'\
        '        if (MASHUP)\n' \
        '           var index = Math.round((d.size /  WORDS[0].size) * 5) -1 ;\n' \
        '        else' \
        '           var index = Math.round((d.size /  Math.round($("#v_VISUALIZATION_ID").width()/8)) * 5);\n'\
        '        return COLORS[index];\n'\
        '    })\n'\
        '    .attr("text-anchor", "middle")\n'\
        '    .attr("transform", function(d) {\n'\
        '        return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";\n'\
        '    })\n'\
        '    .text(function(d) { return d.text; });\n'\
        '}\n'\
        'd3.layout.cloud().size([$("#v_VISUALIZATION_ID").width(), $("#v_VISUALIZATION_ID").height()])\n'\
        ' .words(WORDS)\n'\
        ' .rotate(function() { return ~~(Math.random() * 5) * 30 - 60; })\n'\
        ' .fontSize(function(d) {\n ' \
        '    if (MASHUP) return d.size; \n'\
        '    var words = WORDS;'\
        '    var scale = (d.size / words[0].size);\n'\
        '    if (scale < 0.2) scale = 0.2;\n'\
        '    if (scale > 0.8) scale = 0.8;\n'\
        '    var size = Math.round(scale * Math.round($("#v_VISUALIZATION_ID").width()/8));\n'\
        '    return size;\n'\
        '  })\n'\
        ' .on("end", draw)\n'\
        ' .start();\n'\
        '\n'

        search_result = search_results_collection[0]
        data_dimensions_value = config['data_dimensions'][0]['value']
        facets = [fg for fg in search_result['facet_groups'] if fg['name'] == data_dimensions_value['value']][0]['facets']
        words = [{'text':f['name'], 'size':f['count']} for f in facets]

        if not words:
            return ''

        color_scheme = [e for e in config['elements'] if e['name'] == 'colorscheme'][0]['value']
        colors = self._generate_colors(color_scheme, 100)

        background = [e for e in config['elements'] if e['name'] == 'background'][0]['value']
        if background == 'Dark':
            background = '#333333'
        else:
            background = '#FFFFFF'

        js = js.replace('VISUALIZATION_ID', config['id'])
        js = js.replace('WORDS', json.dumps(words))
        js = js.replace('COLORS', json.dumps(colors))
        js = js.replace('BACKGROUND_COLOR', background)
        js = js.replace('MAX_SIZE', '%i' % max([w['size'] for w in words]))
        js = js.replace('MASHUP', 'false' if [e for e in config['elements'] if e['name'] == 'style'][0]['value'] == 'Standard' else 'true')

        return js

