from django.conf import settings
from urllib import quote
from metalayercore.datapoints.controllers import DataPointController
from datetime import datetime
from logger import Logger
from utils import get_pretty_date

class SearchDataPointParser(object):
    def __init__(self, data_points):
        Logger.Info('%s - SearchDataPointParser.__init__ - started' % __name__)
        Logger.Debug('%s - SearchDataPointParser.__init__ - started with data_point:%s' % (__name__, data_points))
        self.data_points = data_points
        Logger.Info('%s - SearchDataPointParser.__init__ - finished' % __name__)

    def parse_data_points(self):
        Logger.Info('%s - SearchDataPointParser.parse_data_points - started' % __name__)
        data_points_query = 'fq=%s' % '+OR+'.join([self._parse_data_point(dp) for dp in self.data_points])
        Logger.Info('%s - SearchDataPointParser.parse_data_points - finished' % __name__)
        return data_points_query

    def _parse_data_point(self, data_point):
        Logger.Info('%s - SearchDataPointParser._parse_data_point - started' % __name__)
        dpc = DataPointController(data_point)
        data_point_query = 'source_id:%s' % dpc.generate_configured_guid()
        Logger.Info('%s - SearchDataPointParser._parse_data_point - finished' % __name__)
        return data_point_query


class SearchQueryParser(object):
    def __init__(self, query_params):
        Logger.Info('%s - SearchQueryParser.__init__ - started' % __name__)
        Logger.Debug('%s - SearchQueryParser.__init__ - started with query_params:%s' % (__name__, query_params))
        self.params = query_params
        self.not_facets = ['keywords', 'start', 'pagesize']
        Logger.Info('%s - SearchQueryParser.__init__ - finished' % __name__)

    def parse_query(self):
        Logger.Info('%s - SearchQueryParser.parse_query - started' % __name__)
        query = '&'.join([part for part in [self._parse_keywords(), self._parse_pagination(), self._parse_facets()] if part != ''])
        Logger.Info('%s - SearchQueryParser.parse_query - finished' % __name__)
        return query

    def _parse_keywords(self):
        Logger.Info('%s - SearchQueryParser._parse_keywords - started' % __name__)
        keywords_query = 'q=%s' % (quote(self.params['keywords'])) if 'keywords' in self.params and self.params['keywords'] != '' and self.params['keywords'] != None else 'q=*'
        Logger.Info('%s - SearchQueryParser._parse_keywords - finished' % __name__)
        return keywords_query

    def _parse_pagination(self):
        Logger.Info('%s - SearchQueryParser._parse_pagination - started' % __name__)
        parsed_params = []
        for pair in [('start','start'),('pagesize','rows')]:
            if pair[0] in self.params:
                parsed_params.append('%s=%s' % (pair[1], self.params[pair[0]]))
        pagination = '&'.join(parsed_params)
        Logger.Info('%s - SearchQueryParser._parse_pagination - finished' % __name__)
        return pagination

    def _parse_facets(self):
        Logger.Info('%s - SearchQueryParser._parse_facets - started' % __name__)
        parsed_facets = ['fq=%s:%s' % (k, self.params[k]) for k in self.params.keys() if k not in self.not_facets]
        facets = '&'.join(parsed_facets)
        Logger.Info('%s - SearchQueryParser._parse_facets - finished' % __name__)
        return facets

class SearchResultsParser(object):
    def __init__(self, solr_response, request_base, current_request_args):
        Logger.Info('%s - SearchResultsParser.__init__ - started' % __name__)
        self.solr_response = solr_response
        self.request_base = request_base
        self.current_request_args = current_request_args
        Logger.Info('%s - SearchResultsParser.__init__ - finished' % __name__)

    def search_results(self):
        Logger.Info('%s - SearchResultsParser.search_results - started' % __name__)
        result = {
            'content_items': self._extract_content_items(self.solr_response),
            'facet_groups': self._extract_facets(self.solr_response),
            'facet_range_groups': self._extract_facet_ranges(self.solr_response),
            'breadcrumbs': self._extract_breadcrumbs(self.current_request_args),
            'pagination': self._extract_pagination(self.solr_response),
            'keywords': self._extract_keywords(self.solr_response),
        }
        Logger.Info('%s - SearchResultsParser.search_results - finished' % __name__)
        return result

    def _extract_content_items(self, solr_response):
        Logger.Info('%s - SearchResultsParser._extract_content_items - started' % __name__)
        content_items = [self._apply_late_fixes(item) for item in solr_response['response']['docs']]
        Logger.Info('%s - SearchResultsParser._extract_content_items - finished' % __name__)
        return content_items

    def _extract_facets(self, solr_response):
        Logger.Info('%s - SearchResultsParser._extract_facets - started' % __name__)
        facet_groups = []
        if solr_response:
            facet_groups = [{'name':f, 'display_name':f, 'facets':[]} for f in solr_response['facet_counts']['facet_fields'].keys()]
            for fg in facet_groups:
                for x in range(0, len(solr_response['facet_counts']['facet_fields'][fg['name']]), 2):
                    if solr_response['facet_counts']['facet_fields'][fg['name']][x] in ['_none']:
                        continue
                    fg['facets'].append({
                        'name':solr_response['facet_counts']['facet_fields'][fg['name']][x],
                        'count':solr_response['facet_counts']['facet_fields'][fg['name']][x+1],
                        'link':self._construct_facet_link(self.request_base, self.current_request_args, fg['name'], solr_response['facet_counts']['facet_fields'][fg['name']][x])
                    })
        Logger.Info('%s - SearchResultsParser._extract_facets - finished' % __name__)
        return facet_groups

    def _extract_facet_ranges(self, solr_response):
        Logger.Info('%s - SearchResultsParser._extract_facet_ranges - started' % __name__)
        facet_groups = []
        if solr_response:
            facet_groups = [{'name':f, 'display_name':f, 'facets':[]} for f in solr_response['facet_counts']['facet_ranges'].keys()]
            for fg in facet_groups:
                for x in range(0, len(solr_response['facet_counts']['facet_ranges'][fg['name']]['counts']), 2):
                    if solr_response['facet_counts']['facet_ranges'][fg['name']]['counts'][x] in ['_none']:
                        continue
                    fg['facets'].append({
                        'name':solr_response['facet_counts']['facet_ranges'][fg['name']]['counts'][x],
                        'count':solr_response['facet_counts']['facet_ranges'][fg['name']]['counts'][x+1],
                        'link':self._construct_facet_link(self.request_base, self.current_request_args, fg['name'], solr_response['facet_counts']['facet_ranges'][fg['name']]['counts'][x])
                    })
        Logger.Info('%s - SearchResultsParser._extract_facet_ranges - finished' % __name__)
        return facet_groups

    def _extract_breadcrumbs(self, args):
        Logger.Info('%s - SearchResultsParser._extract_breadcrumbs - started' % __name__)
        breadcrumbs = []
        if args:
            breadcrumbs = [{'type':key, 'display_type':key, 'value':args[key], 'link':self._construct_breadcrumb_link(self.request_base, args, key, args[key])} for key in args.keys()]
        Logger.Info('%s - SearchResultsParser._extract_breadcrumbs - finished' % __name__)
        return breadcrumbs

    def _extract_keywords(self, solr_response):
        Logger.Info('%s - SearchResultsParser._extract_keywords - started' % __name__)
        params = solr_response['responseHeader']['params']
        keywords = params['q'] if 'q' in params and params['q'] != '*' else None
        Logger.Info('%s - SearchResultsParser._extract_keywords - finished' % __name__)
        return keywords

    def _extract_pagination(self, solr_response):
        Logger.Info('%s - SearchResultsParser._extract_pagination - started' % __name__)
        pagination = {
            'start':solr_response['response']['start'],
            'pagesize':solr_response['responseHeader']['params']['rows'] if 'rows' in solr_response['responseHeader']['params'] else settings.SOLR_CONFIG['default_page_size'],
            'total':solr_response['response']['numFound']
        }
        Logger.Info('%s - SearchResultsParser._extract_pagination - finished' % __name__)
        return pagination

    def _construct_facet_link(self, request_base, current_request_args, facet_name, facet_value):
        Logger.Info('%s - SearchResultsParser._construct_facet_link - started' % __name__)
        link = '%s?%s' % (request_base, '&'.join(['%s=%s' % (k, current_request_args[k]) for k in current_request_args.keys()]))
        link += '&%s=%s' % (facet_name, facet_value)
        link = link.replace('?&', '?')
        Logger.Info('%s - SearchResultsParser._construct_facet_link - finished' % __name__)
        return link

    def _construct_breadcrumb_link(self, request_base, current_request_args, facet_name, facet_value):
        Logger.Info('%s - SearchResultsParser._construct_breadcrumb_link - started' % __name__)
        link = '%s?%s' % (request_base, '&'.join(['%s=%s' % (k, current_request_args[k]) for k in current_request_args.keys() if k != facet_name and current_request_args[k] != facet_value]))
        link = link if not link.endswith('?') else link[0:-1]
        Logger.Info('%s - SearchResultsParser._construct_breadcrumb_link - finished' % __name__)
        return link

    def _apply_late_fixes(self, item):
        Logger.Info('%s - SearchResultsParser._apply_late_fixes - started' % __name__)
        item['date'] = datetime.fromtimestamp(item['time']).strftime('%Y-%m-%d %H:%M:%S')
        item['pretty_date'] = self._pretty_date(item['time'])
        item['author_display_name'] = '' if item['author_display_name'] == 'none' else item['author_display_name']
        Logger.Info('%s - SearchResultsParser._apply_late_fixes - finished' % __name__)
        return item

    def _pretty_date(self, time=False):
        return get_pretty_date(time)



class SearchQueryAdditionsParser(object):
    def __init__(self, query_additions):
        Logger.Info('%s - SearchQueryAdditionsParser.__init__ - started' % __name__)
        Logger.Info('%s - SearchQueryAdditionsParser.__init__ - started with query_additions:%s' % (__name__, query_additions))
        self.query_additions = query_additions
        Logger.Info('%s - SearchQueryAdditionsParser.__init__ - finished' % __name__)

    def get_formatted_query_additions(self):
        Logger.Info('%s - SearchQueryAdditionsParser.get_formatted_query_additions - started' % __name__)
        additions = []

        basic_facet_fields = [a for a in self.query_additions if a['type'] == 'basic_facet']
        if basic_facet_fields:
            additions.append('&'.join(['facet.field=%s&f.%s.facet.limit=%i' % (a['name'], a['name'], (a['limit'] if 'limit' in a else 100)) for a in basic_facet_fields]))


        range_facet_fields = [a for a in self.query_additions if a['type'] == 'range_facet']
        if range_facet_fields:
            additions.append('&'.join(['facet.range=%s&f.%s.facet.range.gap=%i&f.%s.facet.range.start=%i&f.%s.facet.range.end=%i&f.%s.facet.mincount=0' % (a['name'], a['name'], a['gap'], a['name'], a['start'], a['name'], a['end'], a['name']) for a in range_facet_fields]))

        basic_facet_queries = [a for a in self.query_additions if a['type'] == 'basic_query']
        if basic_facet_queries:
            additions.append('&'.join(['fq=%s:%s' % (a['name'], a['value']) for a in basic_facet_queries]))

        range_facet_queries = [a for a in self.query_additions if a['type'] == 'range_query']
        if range_facet_queries:
            additions.append('&'.join(['fq=%s:[%s TO %s]' % (a['name'], a['range']['start'], a['range']['end']) for a in range_facet_queries]).replace(' ', '%20'))



        Logger.Info('%s - SearchQueryAdditionsParser.get_formatted_query_additions - started' % __name__)
        return '&'.join(additions)


