class BaseDataUploader(object):
    def get_display_config(self):
        pass

    def can_parse_based_on_metadata(self, content_type, file_extension):
        pass

    def can_parse_based_on_test_pass(self, file):
        pass

    def read_file_and_return_errors(self, file):
        pass

    def aggregate_file(self):
        pass

    def clean_up(self):
        pass

class DataUploadError(object):
    _errors = {
        100:"General error reading file",
        101:"File size too large",
        200:"File format does not match extension and metadata",
        201:"The first row of any tabular data must contain header labels",
    }

    def __init__(self, scope, code, debug_info=None):
        self.message = self._errors[code]
        self.code = code
        self.scope = scope
        self.debug_info = debug_info or []