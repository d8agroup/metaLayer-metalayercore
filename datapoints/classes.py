from django.core.cache import cache


class BaseDataPoint(object):
    advanced_feature_markup = '<div class="advanced">This is an advanced feature and requires a bit of technical know-how '\
                              'to use. We\'re working to make this less painful, we promise.</div>'
    def data_point_added(self, config):
        pass

    def data_point_removed(self, config):
        pass

    def perform_post_validation_configuration_changes(self, config):
        return config

    def tick(self, config):
        """Retrieve and format data for this datapoint. The response is a
        dictionary of the following form: {
            'id': 12345,                            # An ID for this piece of content. Implementations must decide if this should be globally unique or not.
            'time': TODO:                           # The time this content was created or last updated.
            'link': 'http://twitter.com/foo/1234',  # A URI to the canonical source.
            'text': [{
                'language': 'en_US',                # Language of the content item.
                'title': 'My Title',                # Title for the item.
                'text': 'Blah blah blah',           # Text for the item.
                'tags': 'Philadelphia, Beer',       # Tags for the item
            }],
            'author': {
                'display_name': 'Rich Schumacher',  # Friendly name of the author.
                'link': 'http://twitter.com/richid',# URI for the author.
                'image': 'http://foo.com/me.jpg',   # URI for author's image.
            },
            'channel': {
                'id': 12345,                        # ID of the channel
                'type': 'twitter',                  # Type of the channel.
                'sub_type': 'search',               # Sub-type of the channel.
            },
            'source': {
                'id': MD5('twitter'),               # ID of the source.
                'display_name': 'Twitter Search',   # Friendly name of the source.
            }
        }
        """
        pass

    def oauth_credentials_are_valid(self, credentials_json):
        return True

    def oauth_poll_for_new_credentials(self, config):
        return None

    def oauth_get_oauth_authenticate_url(self, id):
        return None

    def update_data_point_with_oauth_dependant_config(self, config):
        return config

    def cache_add(self, key, value, timeout=10*60):
        cache.add(key, value, timeout=timeout)

    def cache_get(self, key, default=None):
        return cache.get(key, default)

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
