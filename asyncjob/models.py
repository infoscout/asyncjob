import os
from asyncjob.consts import ASYNCJOB_CELERY_WAIT
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class AsyncJob(models.Model):
    user        = models.ForeignKey(User, null=True, blank=True)
    status      = models.CharField(max_length=24, default=ASYNCJOB_CELERY_WAIT)
    start_date  = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    end_date    = models.DateTimeField(null=True, blank=True)
    job_type    = models.CharField(max_length=32, blank=True, null=True)
    filesize    = models.CharField(max_length=24, null=True, blank=True)
    filename    = models.CharField(max_length=64, null=True, blank=True)
    url         = models.CharField(max_length=768, null=True, blank=True)

    def get_username(self):
        UserModel = getattr(settings, 'ASYNCUP_USER_MODEL', None)
        if UserModel:
            user = UserModel.objects.get(id=self.user_id)
            return user
        else:
            return self.user_id

    def __str__(self):
        value = self.filename or self.id
        return '%s - %s' % (self.user, value)
