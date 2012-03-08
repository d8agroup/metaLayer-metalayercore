from Queue import Queue
import json
import threading
from urllib import urlencode
from urllib2 import Request, urlopen
from metalayercore.actions.classes import BaseAction
from logger import Logger

class Action(BaseAction):
    def get_unconfigured_config(self):
        return {
            'name':'datalayertagging',
            'display_name_short':'Tagging',
            'display_name_long':'Tagging',
            'image_small':'/static/images/thedashboard/actions/tagging_small.png',
            'instructions':'This actions does not need configuring.',
            'configured':True,
            'elements':[],
            'content_properties':{
                'added':[
                    {
                        'display_name':'Tags',
                        'name':'tags',
                        'type':'string'
                    }
                ]
            }
        }

    def run(self, config, content):
        def producer(q, content):
            for item in content:
                thread = TagsGetter(item)
                thread.start()
                q.put(thread, True)
        finished = []
        def consumer(q, content_count):
            while len(finished) < content_count:
                thread = q.get(True)
                thread.join()
                content_id, sentiment = thread.get_result()
                finished.append({'id':content_id, 'tags':sentiment})
        q = Queue(3)
        producer_thread = threading.Thread(target=producer, args=(q, content))
        consumer_thread = threading.Thread(target=consumer, args=(q, len(content)))
        producer_thread.start()
        consumer_thread.start()
        producer_thread.join()
        consumer_thread.join()
        return finished

class TagsGetter(threading.Thread):
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
            url = 'http://api.metalayer.com/s/dashboard/1/tagging'
            post_data = urlencode({ 'text':text })
            request = Request(url, post_data)
            response = urlopen(request)
            response = json.loads(response.read())
            self.result = response['response']['datalayer']['tags'] if response['status'] == 'success' else False
        except Exception, e:
            Logger.Error('%s - run - error %s' % (__name__, e))
            self.result = None

    def extract_content(self):
        text = ''
        if 'title' in self.content:
            text += ' ' + self.content['title']
        if 'text' in self.content:
            for t in self.content['text']:
                text += ' ' + t
        return text

