AsyncJob

	Abstract celery task to run a process, upload output stream to S3, and provide admin monitoring interface.

Usage:

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

Dependencies:
	Django
	Boto
	Celery
	django-celery
	kombu
	South (for included schema migration)
	