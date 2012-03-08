class BaseDataPoint(object):
    advanced_feature_markup = '<div class="advanced">This is an advanced feature and requires a bit of technical know-how '\
                              'to use. We\'re working to make this less painful, we promise.</div>'
    def data_point_added(self, config):
        pass

    def data_point_removed(self, config):
        pass

    def tick(self, config):
        pass
