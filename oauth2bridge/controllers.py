import json
import httplib2
from django.conf import settings
from metalayercore.oauth2bridge.models import (Oauth2StorageObject,
    GoogleOauth2Storage, FacebookOauth2Storage, CredentialsStoreObjects)
from metalayercore.datapoints.controllers import DataPointController


class Oauth2Controller(object):
    """Base class for all provider-specific OAuth2.0 flows. The goal is use a
    mostly declarative syntax when defining new flows by populating the class
    variables below.
    """

    client_id = None
    client_secret = None
    redirect_uri = None
    storage_class = None

    @classmethod
    def GetOauth2AuthorizationUrl(cls, flow):
        flow = cls._EnhanceFlowObject(flow)
        return flow.step1_get_authorize_url(redirect_uri=cls.redirect_uri)

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

    @classmethod
    def PollForNewCredentials(cls, flow):
        storage = Oauth2StorageObject(cls.storage_class, flow.params['state'])
        credentials = storage.get()
        if credentials:
            if not credentials.invalid:
                return credentials
        return None

    @classmethod
    def _EnhanceFlowObject(cls, flow):
        flow.client_id = cls.client_id
        flow.client_secret = cls.client_secret
        flow.params['redirect_uri'] = cls.redirect_uri
        return flow


class GoogleOauth2Controller(Oauth2Controller):
    client_id = settings.OAUTH2_SETTINGS['GoogleOauth2Controller']['client_id']
    client_secret = settings.OAUTH2_SETTINGS['GoogleOauth2Controller']['client_secret']
    redirect_uri = settings.OAUTH2_SETTINGS['GoogleOauth2Controller']['redirect_uri']
    storage_class = GoogleOauth2Storage

    @classmethod
    def HandleOauth2Return(cls, request):
        data_point_id, data_point_type = request.GET.get('state').split('_')
        flow = DataPointController.LoadDataPoint(data_point_type).oauth_get_oauth2_return_handler(data_point_id)
        flow = cls._EnhanceFlowObject(flow)
        credentials = flow.step2_exchange(request.REQUEST)
        storage = Oauth2StorageObject(GoogleOauth2Storage, flow.params['state'])
        storage.put(credentials)


class ImplicitGrantHttpShim(httplib2.Http):
    """Subclass the httplib2's HTTP class in order to intercept an
    application/x-www-form-urlencoded response and return a JSON-encoded
    version. The google_api_python_client module does not appear to work with
    the "Implicit Grant" section[1] of the OAuth 2.0 spec which mandates that
    responses are in the application/x-www-form-urlencoded format, which is
    what Facebook is using[2].

    1. http://tools.ietf.org/html/draft-ietf-oauth-v2-12#section-4.2.2
    2. https://developers.facebook.com/docs/authentication/server-side/

    Note: I've linked to draft 12 of the spec above in [1] because that is
    what Facebook is currently using.
    """
    def request(self, uri, method="GET", body=None, headers=None,
        redirections=httplib2.DEFAULT_MAX_REDIRECTS, connection_type=None):
        """Override the request method to intercept the
        application/x-www-form-urlencoded response and JSON-encode it.
        """
        response, body = super(ImplicitGrantHttpShim, self).request(uri, method, body,
            headers, redirections, connection_type)
        body = dict([_.split("=") for _ in body.split("&")])
        return response, json.dumps(body)


class FacebookOauth2Controller(Oauth2Controller):
    client_id = settings.OAUTH2_SETTINGS['FacebookOauth2Controller']['client_id']
    client_secret = settings.OAUTH2_SETTINGS['FacebookOauth2Controller']['client_secret']
    redirect_uri = settings.OAUTH2_SETTINGS['FacebookOauth2Controller']['redirect_uri']
    storage_class = FacebookOauth2Storage

    @classmethod
    def HandleOauth2Return(cls, request):
        data_point_id, data_point_type = request.GET.get('state').split('_')
        flow = DataPointController.LoadDataPoint(data_point_type).oauth_get_oauth2_return_handler(data_point_id)
        flow = cls._EnhanceFlowObject(flow)
        credentials = flow.step2_exchange(request.REQUEST, http=ImplicitGrantHttpShim())
        storage = Oauth2StorageObject(FacebookOauth2Storage, flow.params['state'])
        storage.put(credentials)
