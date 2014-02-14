from isc_admin import AdminApp
from asyncjob.models import AsyncJob
from asyncjob.admin.model_admin import AsyncJobAdmin

class AsyncJobAdminApp(AdminApp):
    pass

AsyncJobAdminApp.register(AsyncJob, AsyncJobAdmin)
