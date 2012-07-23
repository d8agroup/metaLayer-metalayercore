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
    def __init__(self, file_id, uploaded_file=None,  data_point_type=None, datauploader_name=None):
        self.file_id = file_id
        if uploaded_file:
            self.uploaded_file = uploaded_file
        if data_point_type:
            self.data_point_config = DataPointController.LoadDataPoint(data_point_type).get_unconfigured_config()
        if datauploader_name:
            self.datauploader_name = datauploader_name

    @classmethod
    def AllAvailableUploaders(cls):
        import metalayercore.datauploader.lib as data_uploader_lib
        path = os.path.dirname(data_uploader_lib.__file__)
        data_uploader_directories = [d for d in os.listdir(path) if not re.search(r'\.', d)]
        data_uploaders = [getattr(my_import('metalayercore.datauploader.lib.%s.datauploader' % d), 'DataUploader')() for d in data_uploader_directories]
        return data_uploaders

    @classmethod
    def GetUploaderByName(cls, datauploader_name):
        all_uploaders = cls.AllAvailableUploaders()
        candidate_uploaders = [u for u in all_uploaders if u.get_display_config()['name'] == datauploader_name]
        return candidate_uploaders[0] if candidate_uploaders and len(candidate_uploaders) == 1 else None

    def is_valid(self):
        errors = []
        try:
            uploaded_file_size = self.uploaded_file.size
            if uploaded_file_size > 10485760:
                errors.append('The file you uploaded is too large.')
        except Exception:
            errors.append('We could not read that file.')
        return bool(errors), errors

    def list_available_uploaders(self):
        all_uploaders = DataUploadController.AllAvailableUploaders()
        file_content_type = self.uploaded_file.content_type
        file_extension = self.uploaded_file.name.split('.')[-1]
        available_uploaders = [u for u in all_uploaders if u.can_parse_based_on_metadata(file_content_type, file_extension)]
        available_uploaders_config = [u.get_display_config() for u in available_uploaders]
        return available_uploaders_config

    def run_datauploader(self):
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
            item['channel'] = { 'type':self.data_point_config['type'], 'sub_type':self.data_point_config['sub_type'], 'id':channel_id }
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