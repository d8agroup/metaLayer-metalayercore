from metalayercore.datapoints.controllers import DataPointController
from oauth2client.file import Storage
from django.conf import settings
import time

class GoogleOauth2Controller(object):
    @classmethod
    def _EnhanceFlowObject(cls, flow):
        flow.client_id = settings.OAUTH2_SETTINGS['GoogleOauth2Controller']['client_id']
        flow.client_secret = settings.OAUTH2_SETTINGS['GoogleOauth2Controller']['client_secret']
        flow.params['redirect_uri'] = settings.OAUTH2_SETTINGS['GoogleOauth2Controller']['redirect_uri']
        return flow

    @classmethod
    def GetOauth2AuthorizationUrl(cls, flow):
        flow = cls._EnhanceFlowObject(flow)
        return flow.step1_get_authorize_url(redirect_uri=flow.params['redirect_uri'])

    @classmethod
    def PollForNewCredentials(cls, flow):
        while 1:
            storage = Storage('/tmp/%s.json' % flow.params['state'])
            credentials = storage.get()
            if credentials and not credentials.invalid:
                return credentials
            time.sleep(2)

    @classmethod
    def HandleOauth2Return(cls, request):
        data_point_id, data_point_type = request.GET.get('state').split('_')
        flow = DataPointController.LoadDataPoint(data_point_type).oauth_get_oauth2_return_handler(data_point_id)
        flow = cls._EnhanceFlowObject(flow)
        credentials = flow.step2_exchange(request.REQUEST)
        storage = Storage('/tmp/%s.json' % flow.params['state'])
        storage.put(credentials)


