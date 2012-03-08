from urllib2 import urlopen
from django.conf import settings
from logger import Logger
from metalayercore.search.parsers import SearchDataPointParser, SearchQueryParser, SearchResultsParser, SearchQueryAdditionsParser
from django.utils import simplejson as json

class SearchController(object):
    def __init__(self, configuration):
        Logger.Info('%s - SearchController.__init__ - started' % __name__)
        Logger.Debug('%s - SearchController.__init__ - started with configuration:%s' % (__name__, configuration))
        self.configuration = configuration
        Logger.Info('%s - SearchController.__init__ - finished' % __name__)

    def run_search_and_return_results(self, search_query_additions=None):
        Logger.Info('%s - SearchController.run_search_and_return_results - started' % __name__)
        data_points = self.configuration['data_points']
        sdpp = SearchDataPointParser(data_points)
        search_filters = self.configuration['search_filters']
        sqp = SearchQueryParser(search_filters)
        search_components = [
            settings.SOLR_CONFIG['solr_params'],
            '&'.join(['facet.field=%s' % facet for facet in settings.SOLR_CONFIG['solr_facets'].keys() if settings.SOLR_CONFIG['solr_facets'][facet]['enabled']]),
            sdpp.parse_data_points(),
            sqp.parse_query()
        ]
        if search_query_additions:
            sqap = SearchQueryAdditionsParser(search_query_additions)
            query_additions = sqap.get_formatted_query_additions()
            search_components.append(query_additions)
        search_url = '%s/select/?%s' % (settings.SOLR_CONFIG['solr_url'], '&'.join(search_components))
        Logger.Debug('%s - SearchController.run_search_and_return_results - contacting solr with url:%s' % (__name__, search_url))
        response = urlopen(search_url).read()
        response = json.loads(response)
        srp = SearchResultsParser(response, '/search', search_filters)
        search_results = srp.search_results()
        Logger.Info('%s - SearchController.run_search_and_return_results - finished' % __name__)
        return search_results

