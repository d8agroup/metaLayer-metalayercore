class BaseDataUploader(object):
    def get_display_config(self):
        pass

    def get_content_item_template(self):
        pass

    def can_parse_based_on_metadata(self, content_type, file_extension):
        pass

    def can_parse_based_on_test_pass(self, file):
        pass

    def read_file_and_return_content(self, file):
        pass