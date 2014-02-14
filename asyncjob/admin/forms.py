from django import forms
from isc_admin.forms import ChangeListSearchForm
    
class AsyncJobListForm(ChangeListSearchForm):
    def __init__(self, *args, **kwargs):
        super(AsyncJobListForm, self).__init__(*args, **kwargs)

    user = forms.CharField(label='Username')
    status = forms.CharField()
