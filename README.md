# AsyncJob

Abstract celery task to run a process, upload output stream to S3, with admin monitoring interface.

### Implementation

Extend AsyncJob class and define syncjob() method to output either a string or file typed object.

The AsyncJob will upload this output to S3 and provide admin monitoring as the process runs.

AsyncJob Django Settings:

    ASYNCJOB_S3_HTTP_BASE = 'https://s3.amazonaws.com/'
    ASYNCUP_S3_BUCKET_NAME = 'path.to.your.s3.bucket'
    ASYNCJOB_S3_BUCKET_FOLDER = 'sub.folder.name' 

Boto Dependency Django Settings:

    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY

See the Monitoring: /admin/asyncjob/asyncjob/

Logging will use 'asyncjob' django logger.


### Python dependencies

* Django
* Boto
* Celery
* django-celery
* kombu
* South (for included schema migration)


### Example:

    class ExampleTask(AsyncTask):

        input_string = None
        rm_file_after_upload = False # True for resultant file-removal

        def __call__(self, *args, **kwargs):
            """
            Assign your instantiation parameters here.
            override the default self.filename of AsyncJob.id + datestamp
            Be sure to end with a call to super()
            """
    
            self.input_string = kwargs['input_string']

            filename = input_string[:12]
            self.filename = '%s.csv' % (filename)

            super(ExampleTask, self).__call__(*args, **kwargs)

        def asynctask(self):
            """
            This is where the heavy lifting of your task takes place.
            Return a string or file typed object to push to S3.
            """
            input_string = self.input_string
            resultant = complex_function(input_string)
            return resultant

        def after_return(self, status, retval, task_id, args, kwargs, einfo):
            """
            Celery Handler called after the task returns.
            http://celery.readthedocs.org/en/latest/userguide/tasks.html#handlers
            Can evaluate task state, perform emailing, etc...
            """
            if retval == ASYNCJOB_COMPLETE:
                export_success_email(self.job.user.email, self.job.url)
            elif self.job.user and self.job.user.email:
                export_fail_email(self.job.user.email)

    
    ExampleTask().start(user=user, job_type='Demo', input_string='123abc')
