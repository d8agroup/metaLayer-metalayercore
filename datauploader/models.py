import datetime
from django.db import models
from djangotoolbox.fields import ListField, EmbeddedModelField, DictField

class DataUploadRecord(models.Model):
    file_id = models.TextField()
    file_path = models.TextField()
    created = models.DateTimeField()
    progress = ListField(EmbeddedModelField('DataUploadProgress'))
    finished = models.BooleanField(default=False)

    def record_progress(self, data_upload_progress):
        self.progress.append(data_upload_progress)
        if data_upload_progress.progress == 1.0:
            self.finished = True
        self.save()

class DataUploadProgress(models.Model):
    created = models.DateTimeField()
    stage = models.TextField()
    progress = models.FloatField()
    errors = DictField()
    extensions = DictField()


    @classmethod
    def Create(cls, stage, extensions=None):
        _progress = {
            'start': 0.0,
            'looking_for_parser':0.1,
            'candidate_parsers_found':0.2,

            'waiting_user_parser_choice':0.5,
            'beginning_parse':0.6,
            'no_parser_based_on_metadata':1,
            'all_parsers_failed_to_parse':1
        }
        created = datetime.datetime.now()
        progress = _progress[stage]
        dup = DataUploadProgress(
            stage=stage,
            created=created,
            progress=progress,
            extensions=extensions or {}
        )
        return dup


