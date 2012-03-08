class BaseAction(object):
    advanced_feature_markup = '<div class="advanced">This is an advanced feature and requires a bit of technical know-how ' \
                              'to use. We\'re working to make this less painful, we promise.</div>'
    def validate_config(self, config):
        return True, []

    def generate_configured_display_name(self, config):
        return config['display_name_long']

    def action_added(self, config):
        pass

    def action_removed(self, config):
        pass