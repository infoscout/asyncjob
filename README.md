# AsyncJob

Abstract celery task to run a process, upload output stream to S3, and provide admin monitoring interface.

### Usage:

	Extend AsyncJob class and define syncjob() method to output either a string or file type object.

	The AsyncJob will upload the output to S3 and provide admin monitoring as the process runs. 

	AsyncJob relies on django.settings:
		ASYNCJOB_S3_HTTP_BASE = 'https://s3.amazonaws.com/'
		ASYNCUP_S3_BUCKET_NAME = 'path.to.your.s3.bucket'
		ASYNCJOB_S3_BUCKET_FOLDER = 'sub.folder.name' 

	Logging will use 'asyncjob' django logger.

	Boto usage relies on django.settings:
		AWS_ACCESS_KEY_ID
		AWS_SECRET_ACCESS_KEY


### Dependencies:

	Django
	Boto
	Celery
	django-celery
	kombu
	South (for included schema migration)


### Example Usage

    class ExampleTask(AsyncTask):
    
        input_string = None
        hashed_string = None
        rm_file_after_upload = True
    
        def __call__(self, user_obj, input_string, *args, **kwargs):
            """
            Assign your instantiation parameters here.
            Be sure to assign self.user to a User object & call the super() class.
            """
            from django.contrib.auth.models import User
            assert isinstance(user, User)
            self.user = user
    
            self.input_string = input_string
            filename = input_string[:12]
            self.filename = '%s.csv' % (filename)
    
            super(ExampleTask, self).__call__(*args, **kwargs)
    
        def after_return(self, status, retval, task_id, args, kwargs, einfo):
            """
            Handler called after the task returns.
            """
            if retval == ASYNCJOB_COMPLETE:
                export_success_email(self.job.user.email, self.job.url)
            elif self.job and self.job.user and self.job.user.email:
                export_fail_email(self.job.user.email)
    
        def asynctask(self):
            input_string = self.input_string
            hashed_string = complex_hash_function(input_string)


