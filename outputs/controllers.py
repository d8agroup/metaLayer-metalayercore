from logger import Logger
from metalayercore.outputs.models import ShortUrl
from utils import my_import
from django.conf import settings

class OutputController(object):
    def __init__(self, output):
        Logger.Info('%s - OutputController.__init__ - started' % __name__)
        Logger.Debug('%s - OutputController.__init__ - started with output:%s' % (__name__, output))
        self.output = output
        Logger.Info('%s - OutputController.__init__ - finished' % __name__)

    @classmethod
    def LoadOutput(cls, output_name):
        Logger.Info('%s - OutputController.LoadOutput - started' % __name__)
        Logger.Info('%s - OutputController.LoadOutput - started with output_name:%s' % (__name__, output_name))
        output = my_import('metalayercore.outputs.lib.%s.output' % output_name)
        output = getattr(output, 'Output')()
        Logger.Info('%s - OutputController.LoadOutput - finished' % __name__)
        return output

    @classmethod
    def GetAllForTemplateOptions(cls, options):
        #TODO: need to take account of options
        Logger.Info('%s - OutputController.GetAllForTemplateOptions - started' % __name__)
        Logger.Debug('%s - OutputController.GetAllForTemplateOptions - started with options:%s' % (__name__, options))
        outputs = [OutputController.LoadOutput(output).get_unconfigured_config() for output in settings.OUTPUTS_CONFIG['enabled_outputs']]
        Logger.Info('%s - OutputController.GetAllForTemplateOptions - started' % __name__)
        return outputs

    def is_valid(self):
        Logger.Info('%s - OutputController.is_valid - started' % __name__)
        output_name = self.output['name']
        output = OutputController.LoadOutput(output_name)
        passed, errors = output.validate_config(self.output)
        Logger.Info('%s - OutputController.is_valid - finished' % __name__)
        return passed, errors

    def generate_url(self):
        Logger.Info('%s - OutputController.generate_url - started' % __name__)
        output_name = self.output['name']
        output = OutputController.LoadOutput(output_name)
        url = output.generate_url(self.output)
        Logger.Info('%s - OutputController.generate_url - finished' % __name__)
        return url

    def generate_output(self, search_results):
        Logger.Info('%s - OutputController.generate_output - started' % __name__)
        Logger.Debug('%s - OutputController.generate_output - started with search_results:%s' % (__name__, search_results))
        output_name = self.output['name']
        output = OutputController.LoadOutput(output_name)
        return_content, content_type = output.generate_output(self.output, search_results)
        Logger.Info('%s - OutputController.generate_output - finished' % __name__)
        return return_content, content_type

    def output_removed(self):
        Logger.Info('%s - OutputController.output_removed - started' % __name__)
        dashboard_id = self.output['dashboard_id']
        collection_id = self.output['collection_id']
        output_id = self.output['id']
        ShortUrl.Delete(dashboard_id, collection_id, output_id)
        Logger.Info('%s - OutputController.output_removed - finished' % __name__)
