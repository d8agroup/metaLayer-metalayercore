import csv
from metalayercore.datauploader.classes import BaseDataUploader, DataUploadError

class DataUploader(BaseDataUploader):
    def can_parse_based_on_metadata(self, content_type, file_extension):
        if content_type not in ['text/csv']:
            return False
        if file_extension not in ['csv']:
            return False
        return True

    def can_parse_based_on_test_pass(self, file):
        try:
            file_as_csv = csv.reader(file.read())
            rows = [r for r in file_as_csv]
        except Exception:
            return False, [DataUploadError('format', 200)]

        first_row_is_header, errors = self._first_row_is_header(rows)
        if not first_row_is_header:
            return False, [DataUploadError('format', 201, debug_info=errors)]

        return True

    def _first_row_is_header(self, rows):
        #No row is longer
        if max([len(r) for r in rows]) > len(rows[0]):
            return False, ['At least one other row is longer than the header row']

        #all are strings
        if any([c for c in rows[0] if type(c) != basestring]):
            return False, ['At least one header value is not a string']

        #each are unique 10% excepted fail rate
        passed = 0.0
        failed = 0.0
        for x in range(1, len(rows)):
            for y in len(rows[0]):
                column_title = rows[0][y]
                try:
                    column_value = rows[x][y]
                except IndexError:
                    continue
                if column_title == column_value:
                    failed += 1
                else:
                    passed += 1
        if not passed or failed/passed > 0.10:
            return False, ['The header names must be unique throughout the column they represent']

        return True, []