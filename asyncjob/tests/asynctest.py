from asyncjob.consts import ASYNCJOB_COMPLETE
from asyncjob.models import AsyncJob
from django.utils import unittest
from celery.registry import tasks

from asyncjob.tasks import TestAsyncJobTask

class AsyncjobTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_asyncjob(self):
        task = TestAsyncJobTask()
        task.delay()
        print AsyncJob.objects.all(), 1
        from django.contrib.auth.models import User
        print User.objects.all(), 2
