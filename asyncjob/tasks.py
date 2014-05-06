from abc import abstractmethod
from boto.exception import S3ResponseError
from boto.s3.key import Key
from django.conf import settings
import boto
import celery
import datetime
import logging
import os

from asyncjob.consts import ASYNCJOB_PROCESSING, ASYNCJOB_UPLOADING, ASYNCJOB_CELERY_WAIT, \
    ASYNCJOB_COMPLETE, ASYNCJOB_ERROR, s3_bucket_name, s3_bucket_folder, s3_url_expiration
from asyncjob.models import AsyncJob

logger = logging.getLogger('asyncjob')

class AsyncTask(celery.Task):
    """
    Inheritable base class to process SyncJob(), uploads to s3, and provides admin interface.

    @param filename: name used to put to S3. Timestamp appended on collision
    @param user_id: django user (optional)
    @param rm_file_after_upload

    @method AsyncTask: override to return a string or file object that will be uploaded to S3. 
    """

    abstract = True
    filename = None
    job = None
    user = None
    rm_file_after_upload = False
    job_type = ''

    @abstractmethod
    def asynctask(self):
        """
        "Override the asynctask() method to return a string or file object.
        """
        pass

    def start(self, *args, **kwargs):
        """
        Synchronously create AsyncJob object and async_task.delay().
        """
        job = AsyncJob()
        job.user = kwargs.get('user', None)
        job.job_type = self.job_type
        job.save()
        self.delay(job=job, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        self.job = kwargs['job']
        self.user = kwargs['user']
        return self.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        try:
            if s3_bucket_name is None or s3_bucket_folder is None:
                logger.debug('AsyncJob #%s Missing S3 settings.' % self.job.id)
                return

            job = self.job
            job.status     = ASYNCJOB_PROCESSING
            job.save()

            # Process data stream
            stream_resource = self.asynctask()

            # Boto upload
            job = AsyncJob.objects.get(id=self.job.id)
            job.status = ASYNCJOB_UPLOADING
            job.save()            

            filename = self.filename if self.filename else self.job.id
            s3_key = self.get_unique_s3_key(filename)

            self.upload_stream_resource(s3_key, stream_resource)

            # Mark complete
            job.filesize = s3_key.size
            job.url = s3_key.generate_url(expires_in=s3_url_expiration)
            job.status = ASYNCJOB_COMPLETE
            job.filename = s3_key.key
            job.end_date = datetime.datetime.now()
            job.save()
            logger.info('AsyncJob #%s Complete!' % self.job.id)

        except Exception as e:
            job.status = ASYNCJOB_ERROR
            job.save()
            logger.error('AsyncJob #%s Failed!' % self.job.id, exc_info=True)
            raise Exception(e) # Re-raise exception to celery handling

        self.job = job
        return ASYNCJOB_COMPLETE

    def upload_stream_resource(self, s3_key, stream_resource):
        if isinstance(stream_resource, basestring):
            s3_key.set_contents_from_string(stream_resource)
        elif isinstance(stream_resource, file):
            stream_resource.seek(0)
            s3_key.set_contents_from_file(stream_resource)
            if self.rm_file_after_upload:
                os.remove(stream_resource.name)
        else:
            logger.error('AsyncJob #%s unknown type:%s' % (self.job.id, type(stream_resource)), exc_info=True)
            raise Exception('Unknown Stream Resource Type.')

    def get_unique_s3_key(self, filename):
        # Boto connection
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(s3_bucket_name)
        s3_key = Key(bucket)

        # Make unique file key-name
        attempts = 0
        while True:
            attempts+=1
            try:
                file_exists = bucket.get_key(filename)
                if file_exists is None:
                    break
            except S3ResponseError:
                if attempts>10:
                    raise
            hash = str(datetime.datetime.now())[16:]
            prefix, file_extension = os.path.splitext(filename)
            filename = prefix +'_'+ hash + file_extension
        s3_key.key = filename
        return s3_key



class TestAsyncJobTask(AsyncTask):

    test_value = None
    CELERY_ALWAYS_EAGER = True

    def __call__(self, test_value, *args, **kwargs):
        from django.contrib.auth.models import User
        user = User.objects.create()
        self.test_value = test_value
        self.user = user
        return self.run(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        assert self.job.status  == ASYNCJOB_COMPLETE

    def asynctask(self):
        # Do some work and return a file() handle or string
        resultant = 1 + 1
        output = str(resultant)
        return output

    def upload_stream_resource(self):
        # disabling s3 upload for testing
        pass


