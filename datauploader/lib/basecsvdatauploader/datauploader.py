from metalayercore.datauploader.classes import BaseDataUploader
from chardet.universaldetector import UniversalDetector
from dateutil import parser as date_parser
from random import randint
from hashlib import md5
import time
import csv

class DataUploader(BaseDataUploader):
    class UnicodeCsvReader(object):
        # http://stackoverflow.com/questions/1846135/python-csv-library-with-unicode-utf-8-support-that-just-works
        chunk_size = 4096
        def __init__(self, f, encoding=None, **kwargs):
            if not encoding:
                chardet_detector = UniversalDetector()
                chardet_detector.reset()
                while 1:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    chardet_detector.feed(chunk)
                    if chardet_detector.done:
                        break
                chardet_detector.close()
                chardet_encoding = chardet_detector.result['encoding']
                encoding = chardet_encoding or 'utf-8'
                f.seek(0)
            self.csv_reader = csv.reader(f, **kwargs)
            self.encoding = encoding

        def __iter__(self):
            return self

        def next(self):
            # read and split the csv row into fields
            row = self.csv_reader.next()
            # now decode
            return [unicode(cell, self.encoding).encode('ascii', 'ignore') for cell in row]

        @property
        def line_num(self):
            return self.csv_reader.line_num

    class UnicodeDictReader(csv.DictReader):
        def __init__(self, f, encoding="utf-8", fieldnames=None, **kwds):
            csv.DictReader.__init__(self, f, fieldnames=fieldnames, **kwds)
            self.reader = DataUploader.UnicodeCsvReader(f, encoding=encoding, **kwds)

    def get_display_config(self):
        return {
            'name':'basecsvdatauploader',
            'display_name':'Tabular Data Uploader',
            'info_message':'Any CSV file data where the first row contains column headers.',
            'image_medium':'/static/images/thedashboard/datauploaders/table_medium.png',
            'detail_level':BaseDataUploader.DETAIL_LEVELS['broad'],
        }

    def get_content_item_template(self):
        return ""\
               "<li style='width:100%;'>"\
               "    <img src='/static/images/thedashboard/datauploaders/table_medium.png' style='width:20px; padding-right:10px;' align='left'/>"\
               "    <p style='float:right;padding-right:10px;'>${pretty_date}</p>"\
               "    <p style='padding-left:30px;'>{{html $data.text}}</p>"\
               "    <ul style='padding-left:30px; margin-top:5px' class='actions'>"\
               "        {{html render_dynamic_content_item_actions_and_extensions($data)}}"\
               "    </ul>"\
               "</li>"

    def can_parse_based_on_metadata(self, content_type, file_extension):
        if content_type not in ['text/csv']:
            return False
        if file_extension not in ['csv']:
            return False
        return True

    def can_parse_based_on_test_pass(self, file):
        def _first_row_is_header(rows):
            if max([len(r) for r in rows]) > len(rows[0]): #No row is longer
                return False, ['At least one other row is longer than the header row']
            if len([c for c in rows[0] if not isinstance(c, basestring)]): #all are strings
                return False, ['At least one header value is not a string']
            if len([c for c in rows[0] if not c]):
                return False, ['At least one header value is empty']
            passed = failed = 0.0
            for x in range(1, len(rows)):
                for y in range(len(rows[0])):
                    try:
                        column_value = rows[x][y]
                    except IndexError:
                        continue
                    if rows[0][y] == column_value: failed += 1
                    else: passed += 1
            if not passed or failed/passed > 0.10:
                return False, ['The header names must be unique throughout the column they represent']
            return True, []

        try:
            file_as_csv = DataUploader.UnicodeCsvReader(file)
            rows = [r for r in file_as_csv]
        except Exception as e:
            return False, ['The file you uploaded is not a CSV file with comma field delimiters and double quote string quoting']
        if not rows:
            return False, ['The file you uploaded is empty.']
        first_row_is_header, errors = _first_row_is_header(rows)
        if not first_row_is_header:
            return False, ['The first row did not contain column headers:'] + errors
        return True, None

    def read_file_and_return_content(self, file):
        def _clean_row(row):
            common_none_values = ['none', 'n/a', 'n/d', 'null']
            for column_count in range(len(row)):
                if isinstance(row[column_count], basestring):
                    if row[column_count].lower() in common_none_values:
                        row[column_count] = None
            return row

        def _is_datetime_column(content_rows, column):
            def _can_be_date_or_time(value):
                try:
                    date_parser.parse(value)
                except ValueError: #string format not recognized
                    return False
                except AttributeError: #not a string
                    return False
                return True
            if not len([c for c in header_row if c['type'] == 'date']): #if no date columns found yet
                number_that_can_be_date = len([r[column] for r in content_rows if _can_be_date_or_time(r[column])])
                if number_that_can_be_date == len(content_rows):
                    return True
            return False

        def _is_float_facet_column(content_rows, column):
            non_float_values = []
            float_value_count = 0
            unique_float_values = []
            for row in range(len(content_rows)):
                value = content_rows[row][column]
                try:
                    float_value = float(value)
                    float_value_count += 1
                    if float_value not in unique_float_values:
                        unique_float_values.append(float_value)
                except Exception:
                    if value and not value in non_float_values:
                        non_float_values.append(value)
            if len(unique_float_values) == 1:
                return False
            if float_value_count == len(content_rows): #everything can be mapped as a float
                return True
            if float_value_count > 0 and not non_float_values:
                return True
            if float_value_count > len(non_float_values):
                return True
            return False

        def _is_text_facet_column(content_rows, column):
            values = {}
            for row in range(len(content_rows)):
                value = content_rows[row][column]
                if not value:
                    continue
                if value in values.keys():
                    values[value] += 1
                else:
                    values[value] = 1
            if values and max([count for count in values.values()]) > 1 < len(values):
                return True
            return False

        def _map_row_to_content(row, header_row, default_time):
            id = md5('%f - %i' % (time.time(), randint(0, 1000000))).hexdigest()
            text = ''
            item_time = default_time
            extensions = {}

            for column_count in range(len(header_row)):
                if not row[column_count]:
                    continue
                column_header = header_row[column_count]
                if column_header['type'] == 'text':
                    text += '<b>%s</b>: %s. ' % (column_header['name'], row[column_count])
                elif column_header['type'] == 'date':
                    try:
                        item_time = time.mktime(date_parser.parse(row[column_count]).timetuple())
                    except Exception:
                        continue
                elif column_header['type'] == 'extensions':
                    facet_name = ''.join(c for c in column_header['name'] if c.isalnum())
                    if column_header['mapping']['type'] == 'float':
                        try:
                            extensions[facet_name] = {
                                'display_name':column_header['name'],
                                'value':float(row[column_count]),
                                'type':'float'
                            }
                        except ValueError:
                            continue
                    else:
                        extensions[facet_name] = {
                            'display_name':column_header['name'],
                            'value':row[column_count],
                            'type':'string'
                        }
            if not text:
                text = 'This item has no text component'
            return {
                'id':id,
                'text':[ { 'title':text[:100], 'text':text } ],
                'time':item_time,
                'extensions':extensions
            }

        all_rows = [r for r in csv.reader(file)]
        header_row = [{'name':''.join([c for c in r if c.isalnum() or c == ' ']), 'type':'', 'mapping':{}} for r in all_rows[0]]
        content_rows = [_clean_row(r) for r in all_rows[1:] if r]

        for column in range(len(header_row)):
            header = header_row[column]
            if _is_datetime_column(content_rows, column):
                header['type'] = 'date'
                continue
            if _is_float_facet_column(content_rows, column):
                header['type'] = 'extensions'
                header['mapping'] = { 'type':'float' }
                continue
            if _is_text_facet_column(content_rows, column):
                header['type'] = 'extensions'
                header['mapping'] = { 'type':'string' }
                continue
            header['type'] = 'text'

        default_time = time.time() - 60
        content = [_map_row_to_content(row, header_row, default_time) for row in content_rows]
        extensions = []
        for item in content:
            for extension_name in item['extensions'].keys():
                extension_type = item['extensions'][extension_name]['type']
                extension_search_friendly_name = 'extensions_%s_%s' % (extension_name, extension_type[0])
                if not [e for e in extensions if e['name'] == extension_search_friendly_name]:
                    extensions.append({
                        'display_name':item['extensions'][extension_name]['display_name'],
                        'name': extension_search_friendly_name,
                        'type':extension_type
                    })

        return content, extensions, None