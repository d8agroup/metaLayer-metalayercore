from Queue import Queue
import json
import threading
from urllib import quote
from urllib2 import urlopen
from metalayercore.actions.classes import BaseAction
from logger import Logger

class Action(BaseAction):
    def get_unconfigured_config(self):
        return {
            'name':'languagedetection',
            'display_name_short':'Language',
            'display_name_long':'Language Detection',
            'image_small':'/static/images/thedashboard/actions/language_small.png',
            'instructions':'This actions does not need configuring.',
            'configured':True,
            'elements':[],
            'content_properties':{
                'added':[
                    {
                        'display_name':'Language',
                        'name':'language',
                        'type':'string'
                    }
                ]
            }
        }

    def run(self, config, content):
        def producer(q, content):
            for item in content:
                thread = LanguageGetter(item)
                thread.start()
                q.put(thread, True)
        finished = []
        def consumer(q, content_count):
            while len(finished) < content_count:
                thread = q.get(True)
                thread.join()
                content_id, language = thread.get_result()
                finished.append({'id':content_id, 'language':language})
        q = Queue(3)
        producer_thread = threading.Thread(target=producer, args=(q, content))
        consumer_thread = threading.Thread(target=consumer, args=(q, len(content)))
        producer_thread.start()
        consumer_thread.start()
        producer_thread.join()
        consumer_thread.join()
        return finished

class LanguageGetter(threading.Thread):
    def __init__(self, content):
        self.content = content
        self.result = None
        threading.Thread.__init__(self)

    def get_result(self):
        return self.content['id'], self.result

    def run(self):
        try:
            text = self.extract_content()
            text = text.encode('ascii', 'ignore')
            url = 'http://ws.detectlanguage.com/0.1/detect?q=%s' % quote(text)
            response = urlopen(url)
            response = json.loads(response.read())
            language = [d for d in response['data']['detections']][0]['language'] if response['data']['detections'] else False
            self.result = language if language != 'xxx' else False
        except Exception, e:
            Logger.Error('%s - LanguageGetter.run - error:%s' % (__name__, e))
            self.result = None

    def extract_content(self):
        text = ''
        if 'title' in self.content:
            text += ' ' + self.content['title']
        if 'text' in self.content:
            for t in self.content['text']:
                text += ' ' + t
        return text

