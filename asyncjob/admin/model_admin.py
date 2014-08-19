from isc_admin import ModelAdmin
from asyncjob.admin.forms import AsyncJobListForm
from asyncjob.consts import s3_bucket_name, s3_bucket_folder, \
    ASYNCJOB_COMPLETE
from asyncjob.models import AsyncJob

class AsyncJobAdmin(ModelAdmin):

    list_display = ('_user','_job_type','_link','start_date','end_date','status', '_filesize')
    ordering = ('-start_date',)
    actions = []

    changelist_search_form_class = AsyncJobListForm
    quick_count = 'id'

    def _filesize(self, obj):
        try:
            out = sizeof_fmt(int(obj.filesize))
        except TypeError:
            out = ''
        return out
    _filesize.short_description = "Filesize"

    def _user(self, obj):
        return str(obj.user)
    _user.allow_tags = False
    _user.short_description = 'Username'

    def _job_type(self, obj):
        return obj.job_type if obj.job_type else ''
    _job_type.short_description = 'Type'

    def _link(self, obj):
        if obj.status == ASYNCJOB_COMPLETE:
            link = obj.url
            name = obj.filename
            output = '<a href="%s">%s</a>' % (link, name)
        else:
            output = ''
        return output
    _link.allow_tags = True
    _link.short_description = 'Download'

    def queryset(self, request):
        #@todo ERROR with isc-admin
        qs = AsyncJob.objects.all()
        #qs = super(AsyncJobAdmin, self).queryset(request)

        if 'user' in self.other_search_fields:
            qs = self.qs_str_filter(qs, 'user__username', self.other_search_fields['user'])
        if 'status' in self.other_search_fields:
            qs = self.qs_str_filter(qs, 'status', self.other_search_fields['status'])
        if 'job_type' in self.other_search_fields:
            qs = self.qs_str_filter(qs, 'job_type', self.other_search_fields['job_type'])
            

        qs.order_by('-start_date')
        return qs

    def has_add_permission(self, request):
        return False


def sizeof_fmt(num):
    for x in ['B','kB','mB','gB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'tB')
