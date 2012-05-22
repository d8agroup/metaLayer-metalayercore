from metalayercore.outputs.classes import BaseOutput

class Output(BaseOutput):
    facet_limit_before_more_link = 3

    def get_unconfigured_config(self):
        return {
            'name':'countoutput',
            'display_name_short':'Counts',
            'display_name_long':'Counts',
            'type':'render',
        }

    def generate_html(self, config, search_results):
        if not search_results:
            return '<div class="loading">Waiting for data <img src="/static/images/thedashboard/loading_circle.gif" />'
        html = "<li style='padding:5px 0; border-bottom:1px dashed #666;'><label>Total Count</label><span style='float:right; font-weight:bold;'>%i</span></li>" % search_results['pagination']['total']
        for facet_group in search_results['facet_groups']:
            if len(facet_group['facets']) > self.facet_limit_before_more_link:
                facet_group_html = "<li style='margin-top:5px;padding:5px 0;'><label>%s<a class='more_link' style='padding-left:10px; font-weight:bold; font-size:%s;'>more &#x25BC;</a></label><ul class='facet_values'>[FACET_VALUES]</ul>" % (facet_group['display_name'], '80%')
            else:
                facet_group_html = "<li style='margin-top:5px;padding:5px 0;'><label>%s</label><ul class='facet_values'>[FACET_VALUES]</ul>" % facet_group['display_name']
            facets_html = ''
            for x in range(len(facet_group['facets'])):
                if x < self.facet_limit_before_more_link:
                    facets_html += "<li style='margin-left:20px;border-bottom:1px dashed #666;padding:5px 0;'><label>%s</label><span style='float:right; font-weight:bold;'>%s</span></li>" % (facet_group['facets'][x]['name'], facet_group['facets'][x]['count'])
                else:
                    facets_html += "<li class='more' style='display:none; margin-left:20px;border-bottom:1px dashed #666;padding:5px 0;'><label>%s</label><span style='float:right; font-weight:bold;'>%s</span></li>" % (facet_group['facets'][x]['name'], facet_group['facets'][x]['count'])
            facet_group_html = facet_group_html.replace('[FACET_VALUES]', facets_html)
            html += facet_group_html

        if 'stats' in search_results:
            for name, value in search_results['stats'].items():
                stats_group_html = "<li style='margin-top:5px;padding:5px 0;'><label>%s</label><ul class='facet_values'>" % name.split('_')[1]
                for name, key in [('Minimum Value', 'min'), ('Maximum Value', 'max'), ('Mean Value', 'mean'), ('Standard Deviation', 'stddev')]:
                    stats_group_html+= "<li style='margin-left:20px;border-bottom:1px dashed #666;padding:5px 0;'><label>%s</label><span style='float:right; font-weight:bold;'>%s</span></li>" % (name, value[key])
                stats_group_html += '</li>'
                html += stats_group_html
        return html
