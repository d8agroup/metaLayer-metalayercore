import os
import re
import time
from metalayercore.aggregator.controllers import AggregationController
from metalayercore.datapoints.controllers import DataPointController
from metalayercore.datauploader.classes import DataUploadError
from metalayercore.datauploader.lib.basecsvdatauploader.datauploader import DataUploader
from hashlib import md5
from utils import my_import

class DataUploadController(object):
    @classmethod
    def AllAvailableUploaders(cls):
        import metalayercore.datauploader.lib as data_uploader_lib
        path = os.path.dirname(data_uploader_lib.__file__)
        data_uploader_directories = [d for d in os.listdir(path) if not re.search(r'\.', d)]
        data_uploaders = [my_import('metalayercore.datauploader.lib.%s.datauploader.DataUploader' % d) for d in data_uploader_directories]
        return data_uploaders

    def __init__(self, uploaded_file, file_id, data_point_type):
        self.uploaded_file = uploaded_file
        self.file_id = file_id
        self.data_point_config = DataPointController.LoadDataPoint(data_point_type).get_unconfigured_config()

    def is_valid(self):
        errors = []
        try:
            uploaded_file_size = self.uploaded_file.size
            if uploaded_file_size > 10485760:
                errors.append(DataUploadError('file', 101))
                return False, errors
        except Exception:
            errors.append(DataUploadError('file', 100))
            return False, errors
        return True, errors

    def parse_uploaded_file(self):
        #TODO this defaults to the basecsvdatauploader at the moment.
        data_uploader = DataUploader()
        if not data_uploader.can_parse_based_on_metadata(self.uploaded_file.content_type, self.uploaded_file.name.split('.')[-1]):
            return None, ['Uploaded files must be in csv format for the time being!']

        passed, errors = data_uploader.can_parse_based_on_test_pass(self.uploaded_file)
        if not passed:
            return None, [e.message for e in errors]

        aggregation_data, extensions, errors = data_uploader.read_file_and_return_errors(self.uploaded_file)
        if errors:
            return None, errors

        channel_id = source_id = md5('%s' % time.time()).hexdigest()
        source_name = 'UserUploadSource_%s' % source_id


        for item in aggregation_data:
            item['source'] = {
                'display_name':source_name,
                'id':source_id
            }
            item['channel'] = {
                'type':self.data_point_config['type'],
                'sub_type':self.data_point_config['sub_type'],
                'id':channel_id
            }

#        start_time = min([c['time'] for c in aggregation_data])
#        end_time = max([c['time'] for c in aggregation_data])

        data_point_config = self._update_data_point(self.data_point_config, channel_id, extensions)

        passed = AggregationController.AggregateUploadedContent(aggregation_data, [], False)
        if passed:
            return data_point_config, None

        return None, ['Sorry, there was a system issue while uploading your data.']

    def _update_data_point(self, data_point, channel_id, extensions):
        for pair in [('channel_id', channel_id)]:
            for element in data_point['elements']:
                if element['name'] == pair[0]:
                    element['value'] = pair[1]

        data_point['meta_data'] = extensions
        data_point['configured'] = True
        return data_point

#    def begin_parse(self):

#        upload_record = DataUploadRecord(
#            file_id=self.file_id,
#            file_path=self.uploaded_file.temporary_file_path,
#            created=datetime.datetime.now()
#        )
#        upload_record.record_progress(DataUploadProgress.Create('start'))
#        upload_record.save()
#
#        upload_record.record_progress(DataUploadProgress.Create('looking_for_parser'))
#        all_uploaders = DataUploadController.AllAvailableUploaders()
#        file_content_type = self.uploaded_file.content_type
#        file_extension = self.uploaded_file.name.split('.')[-1]
#        available_uploaders = [u for u in all_uploaders if u.can_parse_based_on_metadata(file_content_type, file_extension)]
#        if not available_uploaders:
#            upload_record.record_progress(DataUploadProgress.Create('no_parser_based_on_metadata'))
#            upload_record.save()
#            return
#        upload_record.record_progress(DataUploadProgress.Create('candidate_parsers_found'))
#
#        upload_record.record_progress(DataUploadProgress.Create('testing_parser_suitability'))
#        available_uploaders = [{ 'uploader':u, 'can_parse_file':True, 'errors':[]} for u in available_uploaders]
#        for uploader in available_uploaders:
#            can_parse_file, errors = uploader.can_parse_based_on_test_pass(self.uploaded_file)
#            uploader['can_parse_file'] = can_parse_file
#            uploader['errors'] = errors
#        if any([u for u in available_uploaders if u['can_parse_file']]):
#            upload_record.record_progress(
#                DataUploadProgress.Create(
#                    'waiting_user_parser_choice',
#                    { 'available_uploaders': available_uploaders }
#                )
#            )
#        else:
#            upload_record.record_progress(
#                DataUploadProgress.Create(
#                    'all_parsers_failed_to_parse',
#                    { 'available_uploaders': available_uploaders }
#                )
#            )
#        return
#
#    def complete_parse_with_parser(self, ):
#        #TODO this need to be more intiligent
#        upload_record.record_progress(DataUploadProgress.Create('beginning_parse'))
#        uploader = available_uploaders[0]
#        aggregation_data = uploader.read_file_and_return_errors(self.uploaded_file)






