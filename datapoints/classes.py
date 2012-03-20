class BaseDataPoint(object):
    advanced_feature_markup = '<div class="advanced">This is an advanced feature and requires a bit of technical know-how '\
                              'to use. We\'re working to make this less painful, we promise.</div>'
    def data_point_added(self, config):
        pass

    def data_point_removed(self, config):
        pass

    def tick(self, config):
        pass

    def _generate_base_search_start_time_config_element(self, start_time=None):
        if not start_time:
            start_time = '*'
        else:
            start_time = '%i' % int(start_time)
        return {
            'name':'start_time',
            'display_name':'Search Start Date',
            'help':'',
            'type':'hidden',
            'value':start_time
        }
    
    def _generate_base_search_end_time_config_element(self, end_time=None):
        if not end_time:
            end_time = '*'
        else:
            end_time = '%i' % int(end_time)
        return {
            'name':'end_time',
            'display_name':'Search End Date',
            'help':'',
            'type':'hidden',
            'value':end_time
        }
            