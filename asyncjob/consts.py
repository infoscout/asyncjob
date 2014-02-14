from django.conf import settings

# SyncJob States:
ASYNCJOB_PROCESSING = 'Processing'
ASYNCJOB_UPLOADING = 'Uploading File'
ASYNCJOB_COMPLETE = 'Complete'
ASYNCJOB_ERROR = 'Error'

s3_bucket_name = getattr(settings, 'ASYNCJOB_S3_BUCKET_NAME', None)
s3_bucket_folder = getattr(settings, 'ASYNCJOB_S3_BUCKET_FOLDER', None)
s3_http_base = getattr(settings, 'ASYNCJOB_S3_HTTP_BASE', None)
