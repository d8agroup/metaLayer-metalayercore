from django.conf import settings
from logger import Logger
from utils import my_import

class ActionController(object):
    def __init__(self, action):
        Logger.Info('%s - ActionController.__init__ - started' % __name__)
        Logger.Debug('%s - ActionController.__init__ - started with action:%s' % (__name__, action))
        self.action = action
        Logger.Info('%s - ActionController.__init__ - finished' % __name__)

    @classmethod
    def LoadAction(cls, action_name):
        Logger.Info('%s - ActionController.LoadAction - started' % __name__)
        Logger.Info('%s - ActionController.LoadAction - started with action_name:%s' % (__name__, action_name))
        action = my_import('metalayercore.actions.lib.%s.action' % action_name)
        action = getattr(action, 'Action')()
        Logger.Info('%s - ActionController.LoadAction - finished' % __name__)
        return action

    @classmethod
    def GetAllForTemplateOptions(cls, options):
        #TODO: need to take account of options
        Logger.Info('%s - ActionController.GetAllForTemplateOptions - started' % __name__)
        Logger.Debug('%s - ActionController.GetAllForTemplateOptions - started with options:%s' % (__name__, options))
        actions = [ActionController.LoadAction(action).get_unconfigured_config() for action in settings.ACTIONS_CONFIG['enabled_actions']]
        Logger.Info('%s - ActionController.GetAllForTemplateOptions - finished' % __name__)
        return actions

    @classmethod
    def ExtractAPIKeyHelp(cls, action_name):
        Logger.Info('%s - ActionController.ExtractAPIKeyHelp - started' % __name__)
        Logger.Info('%s - ActionController.ExtractAPIKeyHelp - started with action_name:%s' % (__name__, action_name))
        action = my_import('metalayercore.actions.lib.%s.action' % action_name)
        action = getattr(action, 'Action')()
        api_element = [e for e in action.get_unconfigured_config()['elements'] if e['name'] == 'api_key'][0]
        help_text = api_element['help']
        Logger.Info('%s - ActionController.ExtractAPIKeyHelp - finished' % __name__)
        return help_text

    def is_valid(self):
        Logger.Info('%s - ActionController.is_valid - started' % __name__)
        action_name = self.action['name']
        action = ActionController.LoadAction(action_name)
        passed, errors = action.validate_config(self.action)
        Logger.Info('%s - ActionController.is_valid - finished' % __name__)
        return passed, errors

    def run_action(self, content):
        Logger.Info('%s - ActionController.run_action - started' % __name__)
        action_name = self.action['name']
        action = ActionController.LoadAction(action_name)
        raw_results = action.run(self.action, content)
        clean_results = []
        for raw_result in raw_results:
            clean_result = {'id':raw_result['id']}
            for prop in self.action['content_properties']['added']:
                if prop['name'] in raw_result:
                    clean_result[self._search_encode_property(prop)] = self._map_property_default_if_required(raw_result[prop['name']], prop['type'])
            clean_results.append(clean_result)
        Logger.Info('%s - ActionController.run_action - finished' % __name__)
        return clean_results

    def get_configured_display_name(self):
        Logger.Info('%s - ActionController.get_configured_display_name - started' % __name__)
        name = self.action['name']
        action = ActionController.LoadAction(name)
        display_name = action.generate_configured_display_name(self.action)
        Logger.Info('%s - DataPointController.get_configured_display_name - finished' % __name__)
        return display_name

    def action_added(self):
        Logger.Info('%s - ActionController.action_added - started' % __name__)
        name = self.action['name']
        action = ActionController.LoadAction(name)
        action.action_added(self.action)
        Logger.Info('%s - ActionController.action_added - finished' % __name__)

    def action_removed(self):
        Logger.Info('%s - ActionController.action_removed - started' % __name__)
        name = self.action['name']
        action = ActionController.LoadAction(name)
        action.action_removed(self.action)
        Logger.Info('%s - ActionController.action_removed - finished' % __name__)

    def extract_ids_of_content_without_action_applied(self, content_from_solr):
        Logger.Info('%s - ActionController.action_added - started' % __name__)
        Logger.Debug('%s - ActionController.action_added - started with content_from_solr:%s' % (__name__, content_from_solr))
        basic_properties = [prop for prop in self.action['content_properties']['added'] if prop['type'] != 'object']
        search_encoded_basic_properties = [self._search_encode_property(prop) for prop in basic_properties]
        content_ids_without_action_applied = []
        for item in content_from_solr:
            for property_name in search_encoded_basic_properties:
                if property_name not in item and item['id'] not in content_ids_without_action_applied:
                    content_ids_without_action_applied.append(item['id'])
        Logger.Info('%s - ActionController.action_added - finished' % __name__)
        return content_ids_without_action_applied

    def _search_encode_property(self, prop):
        def get_postfix(type):
            if type == 'string': return 's'
            if type == 'location_string': return 's'
            if type == 'location_point': return 's'
            return '_s'
        return 'action_%s_%s_%s' % (self.action['name'], prop['name'], get_postfix(prop['type']))

    def _map_property_default_if_required(self, value, type):
        if value:
            return value
        if type == 'string': return '_none'
        if type == 'location_string': return '_none'
        if type == 'location_point': return '_none'
        return '_s'

