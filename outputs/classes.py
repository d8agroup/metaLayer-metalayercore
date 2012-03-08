from django.conf import settings
from metalayercore.outputs.models import ShortUrl

class BaseOutput(object):
    def generate_url(self, config):
        dashboard_id = config['dashboard_id']
        collection_id = config['collection_id']
        output_id = config['id']
        short_url = ShortUrl.Create(dashboard_id, collection_id, output_id)
        url_identifier = short_url.url_identifier
        url = 'http://%s/o/%s' % (settings.SITE_HOST, url_identifier)
        return url

    def export_clicked(self, config):
        pass