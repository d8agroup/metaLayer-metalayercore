from django.db import models
from hashlib import md5
import time
from logger import Logger

class RunRecord(models.Model):
    key = models.TextField()
    last_success = models.FloatField()

    @classmethod
    def GenerateUniqueKey(cls, actions, data_point):
        unique_key = data_point['type']
        if 'sub_type' in data_point:
            unique_key += data_point['sub_type']
        if 'elements' in data_point:
            unique_key += ''.join([''.join(e['value']) for e in data_point['elements'] if isinstance(e['value'], list)])
            unique_key += ''.join([e['value'] for e in data_point['elements'] if not isinstance(e['value'], list)])
        if actions:
            unique_key += ''.join([a['name'] for a in actions])
        return md5(unique_key).hexdigest()

    @classmethod
    def LastSuccess(cls, data_point, actions=None):
        Logger.Info('%s - RunRecord.LastSuccess - started' % __name__)
        Logger.Debug('%s - RunRecord.LastSuccess - started with data_point:%s and actions:%s' % (__name__, data_point, actions))
        key = cls.GenerateUniqueKey(actions, data_point)
        try:
            run_record = RunRecord.objects.get(key=key)
        except RunRecord.DoesNotExist:
            return None
        last_success = run_record.last_success
        Logger.Info('%s - RunRecord.LastSuccess - started' % __name__)
        return last_success

    @classmethod
    def RecordRun(cls, data_point, actions=None):
        Logger.Info('%s - RunRecord.RecordRun - started' % __name__)
        Logger.Debug('%s - RunRecord.RecordRun - started with data_point:%s and actions:%s' % (__name__, data_point, actions))
        key = cls.GenerateUniqueKey(actions, data_point)
        try:
            run_record = RunRecord.objects.get(key=key)
        except RunRecord.DoesNotExist:
            run_record = RunRecord(key=key)
        run_record.last_success = time.mktime(time.gmtime())
        run_record.save()
        Logger.Info('%s - RunRecord.RecordRun - finished' % __name__)