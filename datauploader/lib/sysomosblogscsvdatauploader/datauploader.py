from metalayercore.datauploader.lib.basecsvdatauploader import datauploader as basecsvdatauploader
from dateutil import parser as date_parser, tz
from hashlib import md5
import time
import csv

class DataUploader(basecsvdatauploader.DataUploader):
    header_row = ["host","link","time","auth","age","gender","country","location","sentiment","title","snippet","contents","uniqueid"]

    def get_display_config(self):
        return {
            'name':'sysomosblogscsvdatauploader',
            'display_name':'Sysomos Blogs Data',
            'info_message':'Blogs data exported from Sysomos in CSV format.',
            'image_medium':'/static/images/thedashboard/datauploaders/sysomos_medium.png',
            'detail_level':basecsvdatauploader.DataUploader.DETAIL_LEVELS['specific'],
        }

    def get_content_item_template(self):
        return ""\
               "<li style='width:100%;'>"\
               "<img src='/static/images/thedashboard/data_points/feed_small.png' style='width:20px; padding-right:10px;' align='left'/>"\
               "<p style='float:right;padding:0 10px;position:relative;top:-2px;'>${pretty_date}</p>"\
               "<p style='padding-left:30px;'>${author_display_name}<span style='font-weight:bold'> ${strip_html($data.title)} - ${display_text_abstract($data.text)}</span></p>"\
               "<ul style='padding-left:30px;' class='actions'>"\
               "    {{if extensions_host_s}}"\
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Host</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_filter' data-facet_name='extensions_host_s' data-facet_value='${extensions_host_s}'>${extensions_host_s}</a>"\
               "       </span>"\
               "    </li>"\
               "    {{/if}}"\
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Sentiment</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_filter' data-facet_name='extensions_sentiment_s' data-facet_value='${extensions_sentiment_s}'>${extensions_sentiment_s}</a>"\
               "       </span>"\
               "    </li>"\
               "    {{if extensions_age_f}}"\
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Age</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_range_filter' data-facet_name='extensions_age_f' data-facet_value='${extensions_age_f}'>${extensions_age_f}</a>"\
               "       </span>"\
               "    </li>"\
               "    {{/if}}"\
               "    {{if extensions_gender_s}}"\
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Gender</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_filter' data-facet_name='extensions_gender_s' data-facet_value='${extensions_gender_s}'>${extensions_gender_s}</a>"\
               "       </span>"\
               "    </li>"\
               "    {{/if}}"\
               "    {{if extensions_country_s}}"\
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Country</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_filter' data-facet_name='extensions_country_s' data-facet_value='${extensions_country_s}'>${extensions_country_s}</a>"\
               "       </span>"\
               "    </li>"\
               "    {{/if}}"\
               "</ul>"\
               "</li>"

    def can_parse_based_on_test_pass(self, file):
        try:
            file_as_csv = super(DataUploader, self).UnicodeCsvReader(file)
        except Exception as e:
            return False, ['The file you uploaded is not a Sysomos CSV file.']

        first_four_rows = []
        for row in file_as_csv:
            first_four_rows.append(row)
            if len(first_four_rows) > 3:
                break

        if len(first_four_rows) != 4:
            return False, ['There is no data in this file.']

        if bool(first_four_rows[0]) or bool(first_four_rows[2]):
            return False, ['The first and third rows should be empty']

        if first_four_rows[3] != self.header_row:
            return False, ['The headers in the forth row should read "%s"' % '","'.join(self.header_row)]

        return True, None

    def read_file_and_return_content(self, file):
        def add_column_headers(r):
            headers = self.header_row
            new_r = {}
            for i in range(len(r)):
                new_r[headers[i]] = r[i]
            return new_r

        content = []
        x = -1
        for row in csv.reader(file):
            x += 1
            if x < 4:#skip the header etc
                continue
            if not row:#skip empty rows
                continue
            row = add_column_headers(row)
            content_item = {
                'id':md5(row['uniqueid']).hexdigest(),
                'text':[{'title':row['title'],'text':[row['contents']]}],
                'time':int(time.mktime(date_parser.parse(row['time']).astimezone(tz.tzutc()).timetuple())),
                'link':row['link'],
                'extensions':{
                    'sentiment':{
                        'type':'string',
                        'value':row['sentiment']
                    }
                }
            }

            age = row.get('age')
            if age:
                try:
                    age = float(age)
                    content_item['extensions']['age'] = {
                        'type':'float',
                        'value':age
                    }
                except Exception:
                    pass
    
            for prop in ['host', 'gender', 'country', 'title']:
                value = row.get(prop)
                if value:
                    content_item['extensions'][prop] = {
                        'type':'string',
                        'value':value
                    }
            content.append(content_item)
    
        extensions = [
            {
                'display_name':'sentiment',
                'name':'extensions_sentiment_s',
                'type':'string',
            },
            {
                'display_name':'host',
                'name':'extensions_host_s',
                'type':'string',
            },
            {
                'display_name':'age',
                'name':'extensions_age_f',
                'type':'float',
            },
            {
                'display_name':'gender',
                'name':'extensions_gender_s',
                'type':'string',
            },
            {
                'display_name':'country',
                'name':'extensions_country_s',
                'type':'string',
            },
            {
                'display_name':'title',
                'name':'extensions_title_s',
                'type':'string',
            },
            {
                'display_name':'snippet',
                'name':'extensions_snippet_s',
                'type':'string',
            }
        ]

        return content, extensions, None