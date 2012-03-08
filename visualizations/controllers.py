from django.conf import settings
from logger import Logger
from utils import my_import

class VisualizationController(object):
    def __init__(self, viz):
        Logger.Info('%s - VisualizationController.__init__ - started' % __name__)
        Logger.Info('%s - VisualizationController.__init__ - started with viz:%s' % (__name__, viz))
        self.viz = viz
        Logger.Info('%s - VisualizationController.__init__ - finished' % __name__)

    @classmethod
    def LoadVisualization(cls, viz_name):
        Logger.Info('%s - VisualizationController.LoadVisualization - started' % __name__)
        Logger.Info('%s - VisualizationController.LoadVisualization - started with action_name:%s' % (__name__, viz_name))
        viz = my_import('metalayercore.visualizations.lib.%s.visualization' % viz_name)
        viz = getattr(viz, 'Visualization')()
        Logger.Info('%s - VisualizationController.LoadVisualization - finished' % __name__)
        return viz

    @classmethod
    def GetAllForTemplateOptions(cls, options):
        #TODO: need to take account of options
        Logger.Info('%s - VisualizationController.GetAllForTemplateOptions - started' % __name__)
        Logger.Debug('%s - VisualizationController.GetAllForTemplateOptions - started with options:%s' % (__name__, options))
        vizs = [VisualizationController.LoadVisualization(v).get_unconfigured_config() for v in settings.VISUALIZATIONS_CONFIG['enabled_visualizations']]
        Logger.Info('%s - VisualizationController.GetAllForTemplateOptions - finished' % __name__)
        return vizs

    def visualization_removed(self):
        Logger.Info('%s - VisualizationController.visualization_removed - started' % __name__)
        viz = VisualizationController.LoadVisualization(self.viz['name'])
        viz.visualization_removed()
        Logger.Info('%s - VisualizationController.visualization_removed - finished' % __name__)

    def get_search_query_additions_collection(self, search_configuration):
        Logger.Info('%s - VisualizationController.get_search_query_additions - started' % __name__)
        viz = VisualizationController.LoadVisualization(self.viz['name'])
        search_query_data = viz.generate_search_query_data(self.viz, search_configuration)
        Logger.Info('%s - VisualizationController.get_search_query_additions - finished' % __name__)
        return search_query_data

    def render_javascript_visualization_for_search_results_collection(self, search_results_collection, search_configuration):
        Logger.Info('%s - VisualizationController.render_javascript_visualization_for_search_results - started' % __name__)
        viz = VisualizationController.LoadVisualization(self.viz['name'])
        javascript = viz.render_javascript_based_visualization(self.viz, search_results_collection, search_configuration)
        Logger.Info('%s - VisualizationController.render_javascript_visualization_for_search_results - finished' % __name__)
        return javascript
