from setuptools import find_packages
from isc_ops.setup_tools import setup, current_version

setup(name='asyncjob',
    packages=find_packages(),  
    include_package_data=True,
    description = 'Abstract celery task to run a process, upload output stream to S3, and provide admin monitoring interface.',
    url = 'http://github.com/infoscout/asynjob',
    version = current_version(),    
    install_requires=[
        'django==1.4',
        'boto==2.8.0',                       # AWS utils
        'south==0.7.6',                      # SQL schema migration 
        'celery==3.0.17',                     # Python queue framework
        'kombu==2.5.11',                      # Also required as part of django-celery
        'django-celery==3.0.11',              # Allows django to run as a message broker
    ]
    # requires: isc-admin
)
