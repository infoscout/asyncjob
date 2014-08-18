from isc_admin.admin_site import AdminApp
from asyncjob.models import AsyncJob
from asyncjob.admin.model_admin import AsyncJobAdmin

class AsyncJobAdminApp(AdminApp):
    pass

AsyncJobAdminApp.register(AsyncJob, AsyncJobAdmin)
