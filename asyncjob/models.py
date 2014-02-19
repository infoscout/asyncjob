import os
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class AsyncJob(models.Model):
    user        = models.ForeignKey(User, null=True, blank=True)
    status      = models.CharField(max_length=24)
    start_date  = models.DateTimeField(null=True, blank=True)
    end_date    = models.DateTimeField(null=True, blank=True)
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