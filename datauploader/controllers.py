from metalayercore.datauploader.models import DataUploadRecord, DataUploadProgress
from metalayercore.aggregator.controllers import AggregationController
from metalayercore.datapoints.controllers import DataPointController
from django.conf import settings
from utils import my_import
from hashlib import md5
import datetime
import time
import re
import os

class DataUploadController(object):
    """
    DataUploadController acts as the main entry point to the DataUploaders package
    """
    def __init__(self, file_id, uploaded_file=None,  data_point_type=None, datauploader_name=None):
        """
        DataUploadController instance constructor

        Notes
        -----
        When constructed with a raw uploaded file, this controller should be instantiated with: file_id and uploaded_file
        When constructed with datauploader choice, this controller should be instantiated with: file_id, data_point_type and datauploader_name

        Arguments
        ---------
        file_id (string, guid): the unique id that applies to this uploaded file
        uploaded_file (file) optional: the uploaded file object taken from POST['FILE'] this should be a django UploadedFile object
        data_point_type (string): The type of the data point that was used to upload this file
        datauploader_name (string): The name of the datauploader chosen to parse the file

        Returns
        -------
        Instance of DataUploadController
        """
        self.file_id = file_id
        if uploaded_file:
            self.uploaded_file = uploaded_file
        if data_point_type:
            self.data_point_config = DataPointController.LoadDataPoint(data_point_type).get_unconfigured_config()
        if datauploader_name:
            self.datauploader_name = datauploader_name

    @classmethod
    def AllAvailableUploaders(cls):
        """
        Class Method: Return the configuration for all DataUploaders available

        Returns
        -------
        List of dict config for all matching DataUploader instances

        Raises
        ------
        AttributeError: if the package and/or module structure on disk is corrupt
        """
        import metalayercore.datauploader.lib as data_uploader_lib
        path = os.path.dirname(data_uploader_lib.__file__)
        data_uploader_directories = [d for d in os.listdir(path) if not re.search(r'\.', d)]
        data_uploaders = [getattr(my_import('metalayercore.datauploader.lib.%s.datauploader' % d), 'DataUploader')() for d in data_uploader_directories]
        return data_uploaders

    @classmethod
    def GetUploaderByName(cls, datauploader_name):
        """
        Class Method: Returns an instance of the DataUploader who matches the datauploader_name argument

        Arguments
        ---------
        datauploader_name (string): the name of the datauploader to be instantiated

        Returns
        -------
        Instance of DataUploader who's name matches the datauploader_name or None if no DataUploader has that name

        Raises
        ------
        AttributeError: if the package and/or module structure on disk is corrupt
        """
        all_uploaders = cls.AllAvailableUploaders()
        candidate_uploaders = [u for u in all_uploaders if u.get_display_config()['name'] == datauploader_name]
        return candidate_uploaders[0] if candidate_uploaders and len(candidate_uploaders) == 1 else None

    def is_valid(self):
        """
        Run basic file checking to ensure the file is a file and that it is less than 10mb in size

        Returns
        -------
        Boolean: File passed basic test
        List(strings): any errors raised
        """
        errors = []
        try:
            uploaded_file_size = self.uploaded_file.size
            if uploaded_file_size > 10485760:
                errors.append('The file you uploaded is too large.')
        except Exception:
            errors.append('We could not read that file.')
        return bool(errors), errors

    def list_available_uploaders(self):
        """
        Return the configuration of all DataUploaders who can parse the subject file based on its metadata

        Returns
        -------
        List[dict]: List of the configuration for all DataUploaders that can parse the file based on its metadata

        Raises
        ------
        AttributeError: if the package and/or module structure on disk is corrupt
        """
        all_uploaders = DataUploadController.AllAvailableUploaders()
        file_content_type = self.uploaded_file.content_type
        file_extension = self.uploaded_file.name.split('.')[-1]
        available_uploaders = [u for u in all_uploaders if u.can_parse_based_on_metadata(file_content_type, file_extension)]
        available_uploaders_config = []
        for uploader in available_uploaders:
            self.uploaded_file.seek(0)
            uploader_config = uploader.get_display_config()
            passed, errors = uploader.can_parse_based_on_test_pass(self.uploaded_file)
            uploader_config['available'] = passed
            uploader_config['errors'] = errors
            available_uploaders_config.append(uploader_config)
        available_uploaders_config = sorted(available_uploaders_config, key=lambda u: u['detail_level'], reverse=True)
        return available_uploaders_config

    def run_datauploader(self):
        """
        Run the selected DataUploader against the persisted file
        """
        upload_record = DataUploadRecord(file_id=self.file_id, created=datetime.datetime.now())
        upload_record.record_progress(DataUploadProgress.Create('start'))
        datauploader = DataUploadController.GetUploaderByName(self.datauploader_name)
        upload_record.record_progress(DataUploadProgress.Create('parsing'))
        with open(os.path.join(settings.MEDIA_ROOT, self.file_id), 'rb+') as uploaded_file:
            passed, errors = datauploader.can_parse_based_on_test_pass(uploaded_file)
            if errors:
                upload_record.record_progress(DataUploadProgress.Create('error', extensions={'errors':errors}))
                return None, errors
        with open(os.path.join(settings.MEDIA_ROOT, self.file_id), 'rb+') as uploaded_file:
            aggregation_data, extensions, errors = datauploader.read_file_and_return_content(uploaded_file)
            if errors:
                upload_record.record_progress(DataUploadProgress.Create('error', extensions={'errors':errors}))
                return None, errors

        upload_record.record_progress(DataUploadProgress.Create('validating'))
        channel_id = source_id = md5('%s' % time.time()).hexdigest()
        source_name = 'UserUploadSource_%s' % source_id
        for item in aggregation_data:
            item['source'] = { 'display_name':source_name, 'id':source_id }
            item['channel'] = { 'type':'customdata', 'sub_type':datauploader.get_display_config()['name'], 'id':channel_id }
        times_list = [c['time'] for c in aggregation_data if 'time' in c]
        start_time = int(min(times_list)) if times_list else None
        end_time = int(max(times_list)) if times_list else None
        data_point_config = self._update_data_point(self.data_point_config, channel_id, extensions, start_time, end_time)

        upload_record.record_progress(DataUploadProgress.Create('aggregating'))
        passed = AggregationController.AggregateUploadedContent(aggregation_data, [], False)
        if not passed:
            errors = ['Sorry, there was a system issue while uploading your data.']
            upload_record.record_progress(DataUploadProgress.Create('error', extensions={'errors':errors}))
            return None, errors

        upload_record.record_progress(DataUploadProgress.Create('finished'))
        return data_point_config, None

    def persist_file(self):
        self.uploaded_file.seek(0) #reset the file if it has been opened for checking
        with open(os.path.join(settings.MEDIA_ROOT, self.file_id), 'wb+') as file:
            for chunk in self.uploaded_file.chunks():
                file.write(chunk)

    def clean_up(self):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.file_id))

    def _update_data_point(self, data_point, channel_id, extensions, start_time, end_time):
        for pair in [('channel_id', channel_id), ('start_time', start_time), ('end_time', end_time)]:
            if pair[1]:
                found = False
                for element in data_point['elements']:
                    if element['name'] == pair[0]:
                        element['value'] = pair[1]
                        found = True
                if not found:
                    data_point['elements'].append({
                        'name':pair[0],
                        'display_name':pair[0],
                        'help':'',
                        'type':'hidden',
                        'value':pair[1]
                    })
        data_point['meta_data'] = extensions
        data_point['configured'] = True
        return data_point