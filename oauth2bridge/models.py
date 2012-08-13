from django.db import models
from djangotoolbox.fields import DictField
from oauth2client.client import Storage, Credentials
from django.utils import simplejson as json

class GoogleOauth2StorageObject(Storage):
    def __init__(self, id):
        self.id = id

    def locked_get(self):
        """
        Retrieve Credential from datastore.

        Returns
        -------
        oauth2client.Credentials: the credentials
        """
        try:
            storage = GoogleOauth2Storage.objects.get(access_id=self.id)
            return storage.get_credentials()
        except GoogleOauth2Storage.DoesNotExist:
            return None

    def locked_put(self, credentials):
        """
        Write a Credentials to the datastore.

        Arguments
        ---------
        credentials: Credentials, the credentials to store.
        """
        try:
            storage = GoogleOauth2Storage.objects.get(access_id=self.id)
        except GoogleOauth2Storage.DoesNotExist:
            storage = GoogleOauth2Storage(access_id=self.id)
        storage.set_credentials(credentials)
        storage.save()

    def locked_delete(self):
        """
        Delete Credentials from the datastore.
        """
        try:
            storage = GoogleOauth2Storage.objects.get(access_id=self.id)
            storage.delete()
        except GoogleOauth2Storage.DoesNotExist:
            return

class GoogleOauth2Storage(models.Model):
    access_id = models.CharField(max_length=256)
    credentials = models.TextField()

    def set_credentials(self, raw_credentials):
        credentials = raw_credentials.to_json()
        self.credentials = credentials

    def get_credentials(self):
        credentials = Credentials.new_from_json(self.credentials)
        return credentials

class CredentialsStoreObjects(models.Model):
    key = models.TextField()
    store = models.TextField()