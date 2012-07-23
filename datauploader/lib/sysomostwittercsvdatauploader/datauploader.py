from metalayercore.datauploader.lib.basecsvdatauploader import datauploader as basecsvdatauploader
from dateutil import parser as date_parser, tz
from hashlib import md5
import time
import csv

class DataUploader(basecsvdatauploader.DataUploader):
    def get_display_config(self):
        return {
            'name':'sysomostwittercsvdatauploader',
            'display_name':'Sysomos Twitter Data',
            'info_message':'Twitter search data exported from Sysomos in CSV format.',
            'image_medium':'/static/images/thedashboard/datauploaders/sysomos_medium.png',
        }

    def get_content_item_template(self):
        return ""\
               "<li style='width:100%;'>"\
               "<a href='${author_link}'>"\
               "<img src='/static/images/thedashboard/data_points/twitter_small.png' style='width:20px; padding:1px;' align='left' class='helper_corner tool_tip' title='<b>${author_display_name}</b> - click to view their profile on Twitter' />"\
               "</a>"\
               "<p style='float:left; padding:2px 0 0 8px;font-weight:bold;width:40%;overflow:hidden;height:12px;'>${author_display_name}</p>"\
               "<p style='margin-bottom:2px;text-align:right'>"\
               "<span style='position:relative;bottom:4px;right:10px;'>${pretty_date}</span>"\
               "<img src='/static/images/thedashboard/data_points/twitter_small.png' style='width:15px;'/>"\
               "</p>"\
               "<a href='${link}'><p style='padding-left:30px;' class='tool_tip' title='click to see original post on Twitter+'>${title}</p></a>"\
               "<ul style='padding-left:30px;' class='actions'>"\
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Twitter Username</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_filter' data-facet_name='extensions_twitterusername_s' data-facet_value='${extensions_twitterusername_s}'>${extensions_twitterusername_s}</a>"\
               "       </span>"\
               "    </li>"\
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Sentiment</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_filter' data-facet_name='extensions_sentiment_s' data-facet_value='${extensions_sentiment_s}'>${extensions_sentiment_s}</a>"\
               "       </span>"\
               "    </li>"\
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Followers</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_filter' data-facet_name='extensions_followers_s' data-facet_value='${extensions_followers_s}'>${extensions_followers_f}</a>"\
               "       </span>"\
               "    </li>"\
               "    <li class='action_values' style='margin-top:5px;'>"\
               "       <label>Following</label>"\
               "       <span style='font-weight:bold;'>"\
               "           <a class='action_inline_filter' data-facet_name='extensions_following_s' data-facet_value='${extensions_following_s}'>${extensions_following_f}</a>"\
               "       </span>"\
               "    </li>"\
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

        if first_four_rows[3] != ["host","link","time","auth","follower","following","age","gender","country","location","sentiment","contents","uniqueid"]:
            return False, ['The headers in the forth row should read "host","link","time","auth","follower","following","age","gender","country","location","sentiment","contents","uniqueid"']

        return True, None

    def read_file_and_return_content(self, file):
        def add_column_headers(r):
            headers = ['host', 'link', 'time', 'auth', 'follower', 'following', 'age', 'gender', 'country', 'location', 'sentiment', 'content', 'uniqueid']
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
                'id': md5(row['uniqueid']).hexdigest(), 
                'text': [ {'title': '%s - %s' % (row['content'].decode('utf-8'), row['location'].decode('utf-8')), }],
                'time': int(time.mktime(date_parser.parse(row['time']).astimezone(tz.tzutc()).timetuple())),
                'link': row['link'],
                'author': {
                    'display_name': row['host'].replace('http://twitter.com/', '').strip(),
                    'link': row['host'],
                    'image': 'http://purl.org/net/spiurl/%s' % row['host'].replace('http://twitter.com/', '').strip(), 
                },
                'extensions': {
                    'sentiment': {
                        'type': 'string', 
                        'value': row['sentiment']
                    },
                    'twitterusername': {
                        'type': 'string',
                        'value': row['host'].replace('http://twitter.com/', '').strip(), 
                    }
                }
            }
            try:
                followers = float(row['follower'])
                content_item['extensions']['followers'] = {'type':'float', 'value':followers}
            except ValueError:
                pass
            try:
                following = float(row['following'])
                content_item['extensions']['following'] = {'type':'float', 'value':following}
            except ValueError:
                pass

            content.append(content_item)
    
        extensions = [
            {
                'display_name':'sentiment',
                'name':'extensions_sentiment_s',
                'type':'string',
            },
            {
                'display_name':'twitterusername',
                'name':'extensions_twitterusername_s',
                'type':'string',
            },
            {
                'display_name':'followers',
                'name':'extensions_followers_f',
                'type':'float',
            },
            {
                'display_name':'following',
                'name':'extensions_following_f',
                'type':'float',
            }
        ]

        return content, extensions, None