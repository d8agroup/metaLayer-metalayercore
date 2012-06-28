import datetime
from django.conf import settings
import os
import re
from metalayercore.datauploader.classes import DataUploadError
from metalayercore.datauploader.models import DataUploadRecord, DataUploadProgress
from utils import async, my_import

class DataUploadController(object):
    @classmethod
    def AllAvailableUploaders(cls):
        import metalayercore.datauploader.lib as data_uploader_lib
        path = os.path.dirname(data_uploader_lib.__file__)
        data_uploader_directories = [d for d in os.listdir(path) if not re.search(r'\.', d)]
        data_uploaders = [my_import('metalayercore.datauploader.lib.%s.datauploader.DataUploader' % d) for d in data_uploader_directories]
        return data_uploaders

    def __init__(self, uploaded_file, file_id):
        self.uploaded_file = uploaded_file
        self.file_id = file_id

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

    @async
    def begin_parse(self):
        upload_record = DataUploadRecord(
            file_id=self.file_id,
            file_path=self.uploaded_file.temporary_file_path,
            created=datetime.datetime.now()
        )
        upload_record.record_progress(DataUploadProgress.Create('start'))
        upload_record.save()
        yield

        upload_record.record_progress(DataUploadProgress.Create('looking_for_parser'))
        all_uploaders = DataUploadController.AllAvailableUploaders()
        file_content_type = self.uploaded_file.content_type
        file_extension = self.uploaded_file.name.split('.')[-1]
        available_uploaders = [u for u in all_uploaders if u.can_parse_based_on_metadata(file_content_type, file_extension)]
        if not available_uploaders:
            upload_record.record_progress(DataUploadProgress.Create('no_parser_based_on_metadata'))
            upload_record.save()
            return
        upload_record.record_progress(DataUploadProgress.Create('candidate_parsers_found'))

        upload_record.record_progress(DataUploadProgress.Create('testing_parser_suitability'))
        available_uploaders = [{ 'uploader':u, 'can_parse_file':True, 'errors':[]} for u in available_uploaders]
        for uploader in available_uploaders:
            can_parse_file, errors = uploader.can_parse_based_on_test_pass(self.uploaded_file)
            uploader['can_parse_file'] = can_parse_file
            uploader['errors'] = errors
        if any([u for u in available_uploaders if u['can_parse_file']]):
            upload_record.record_progress(
                DataUploadProgress.Create(
                    'waiting_user_parser_choice',
                    { 'available_uploaders': available_uploaders }
                )
            )
        else:
            upload_record.record_progress(
                DataUploadProgress.Create(
                    'all_parsers_failed_to_parse',
                    { 'available_uploaders': available_uploaders }
                )
            )
        return

    def complete_parse_with_parser(self, ):
        #TODO this need to be more intiligent
        upload_record.record_progress(DataUploadProgress.Create('beginning_parse'))
        uploader = available_uploaders[0]
        aggregation_data = uploader.read_file_and_return_errors(self.uploaded_file)






