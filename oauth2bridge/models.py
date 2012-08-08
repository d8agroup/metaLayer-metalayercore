from django.db import models
from oauth2client.django_orm import CredentialsField

class GoogleOauth2StorageObject(object):
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
            return storage.credentials
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
            storage = GoogleOauth2Storage.objects.get(access_id=id)
        except GoogleOauth2Storage.DoesNotExist:
            storage = GoogleOauth2Storage(access_id=self.id)
        storage.credentials = credentials
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
    credentials = CredentialsField()