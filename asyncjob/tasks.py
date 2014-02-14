from abc import abstractmethod
from boto.exception import S3ResponseError
from boto.s3.key import Key
from celery.registry import tasks
from django.conf import settings
import boto
import celery
import datetime
import logging
import os

from asyncjob.consts import ASYNCJOB_PROCESSING, ASYNCJOB_UPLOADING, \
    ASYNCJOB_COMPLETE, ASYNCJOB_ERROR, s3_bucket_name, s3_bucket_folder
from asyncjob.models import AsyncJob

logger = logging.getLogger('asyncjob')

class AsyncTask(celery.Task):
    """
    Inheritable base class to process SyncJob(), uploads to s3, and provides admin interface.

    @param filename: name used to put to S3. Timestamp appended on collision
    @param user_id: django user (optional)
    
    @method AsyncTask: override to return a string or file object that will be written to S3. 
    """

    filename = None
    user_id = None

    @abstractmethod
    def asynctask(self):
        """
        "Override the SyncJob() method to return a string or file object.
        """
        pass
        
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
            hash = str(datetime.datetime.now())[:-1]
            prefix, file_extension = os.path.splitext(filename)
            filename = prefix + hash + file_extension
        s3_key.key = filename
        return s3_key

    def run(self):
        if s3_bucket_name is None or s3_bucket_folder is None:
            logger.debug('AsyncJob #%s Missing S3 settings.' % job_id)
            return

        job = AsyncJob()
        job.user_id    = self.user_id
        job.status     = ASYNCJOB_PROCESSING
        job.start_date = datetime.datetime.now()
        job.save()
        job_id = job.id

        try:
            # Process data stream
            stream_resource = self.AsyncTask()    

            # Boto upload
            job = AsyncJob.objects.get(id=job_id)
            job.status = ASYNCJOB_UPLOADING
            job.save()            
    
            filename = self.filename if self.filename else job_id
            s3_key = self.get_unique_s3_key(filename)

            if isinstance(stream_resource, basestring):
                s3_key.set_contents_from_string(stream_resource)
            elif isinstance(stream_resource, file):
                s3_key.set_contents_from_stream(stream_resource)
            else:
                raise

            # Mark complete
            job.filesize = s3_key.size 
            job.status = ASYNCJOB_COMPLETE
            job.filename = s3_key.key
            job.end_date = datetime.datetime.now()
            job.save()
            logger.debug('AsyncJob #%s Complete!' % job_id)
            return 'Success'

        except Exception as e:
            logger.error('AsyncJob #%s Failed!' % job_id, exc_info=True)
            job.status = ASYNCJOB_ERROR
            job.save()

tasks.register(AsyncTask)
