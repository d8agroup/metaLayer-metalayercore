from metalayercore.oauth2bridge.models import GoogleOauth2StorageObject, CredentialsStoreObjects
from metalayercore.datapoints.controllers import DataPointController
from django.conf import settings
import time

class Oauth2Controller(object):
    @classmethod
    def PersistCredentialsStore(cls, id, store_json):
        try:
            store_object = CredentialsStoreObjects.objects.get(key=id)
        except CredentialsStoreObjects.DoesNotExist:
            store_object = CredentialsStoreObjects(key=id)
        store_object.store = store_json
        store_object.save()

    @classmethod
    def RetrieveCredentialsStore(cls, id):
        try:
            store_object = CredentialsStoreObjects.objects.get(key=id)
            return store_object.store
        except CredentialsStoreObjects.DoesNotExist:
            return None

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
            storage = GoogleOauth2StorageObject(flow.params['state'])
            credentials = storage.get()
            if credentials:
                if not credentials.invalid:
                    return credentials
            time.sleep(2)

    @classmethod
    def HandleOauth2Return(cls, request):
        data_point_id, data_point_type = request.GET.get('state').split('_')
        flow = DataPointController.LoadDataPoint(data_point_type).oauth_get_oauth2_return_handler(data_point_id)
        flow = cls._EnhanceFlowObject(flow)
        credentials = flow.step2_exchange(request.REQUEST)
        storage = GoogleOauth2StorageObject(flow.params['state'])
        storage.put(credentials)
