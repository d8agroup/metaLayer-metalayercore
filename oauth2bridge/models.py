from django.db import models
from oauth2client.client import Storage, Credentials


class Oauth2StorageObject(Storage):
    def __init__(self, implementation, access_id):
        """Class to manage inserting and retrieving credential objects for the
        various OAuth-enabled resource providers. All actual work is delegated
        to the concrete model classes which are passed in as a parameter.

        `implementation` must be a class, not an instance
        """
        self.access_id = access_id
        self._impl = implementation

    def locked_get(self):
        """
        Retrieve Credential from datastore.

        Returns
        -------
        oauth2client.Credentials: the credentials
        """
        try:
            storage = self._impl.objects.get(access_id=self.access_id)
            return storage.get_credentials()
        except self._impl.DoesNotExist:
            return None

    def locked_put(self, credentials):
        """
        Write a Credentials to the datastore.

        Arguments
        ---------
        credentials: Credentials, the credentials to store.
        """
        try:
            storage = self._impl.objects.get(access_id=self.access_id)
        except self._impl.DoesNotExist:
            storage = self._impl(access_id=self.access_id)
        storage.set_credentials(credentials)
        storage.save()

    def locked_delete(self):
        """
        Delete Credentials from the datastore.
        """
        try:
            storage = self._impl.objects.get(access_id=self.access_id)
            storage.delete()
        except self._impl.DoesNotExist:
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


class FacebookOauth2Storage(models.Model):
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
