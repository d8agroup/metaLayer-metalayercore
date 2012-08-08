from oauth2client.file import Storage
import time
from metalayercore.datapoints.controllers import DataPointController

class GoogleOauth2Controller(object):
    @classmethod
    def GetOauth2AuthorizationUrl(cls, flow):
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
        flow.redirect_uri = flow.params['redirect_uri']
        credentials = flow.step2_exchange(request.REQUEST)
        storage = Storage('/tmp/%s.json' % flow.params['state'])
        storage.put(credentials)


