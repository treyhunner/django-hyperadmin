from django.utils.encoding import force_unicode
from django import forms

from hyperadmin.hyperobjects import ResourceItem


class ListForm(forms.Form):
    '''
    hyperadmin knows how to serialize forms, not models.
    So for the list display we need a form
    '''
    
    def __init__(self, **kwargs):
        self.instance = kwargs.pop('instance', None)
        self.resource = kwargs.pop('resource')
        super(ListForm, self).__init__(**kwargs)
        if self.resource.list_display:
            for display in self.resource.list_display:
                label = display
                if label == '__str__':
                    label = self.resource.resource_name
                self.fields[display] = forms.CharField(label=label)
                if self.instance:
                    if hasattr(self.instance, display):
                        try:
                            val = getattr(self.instance, display)
                        except:
                            val = ''
                    elif hasattr(self.resource, display):
                        try:
                            val = getattr(self.resource, display)(self.instance)
                        except:
                            val = ''
                    else:
                        val = '' #TODO raise ImproperlyConfigured
                    if callable(val):
                        try:
                            val = val()
                        except:
                            val = ''
                    self.initial[display] = force_unicode(val)
        else:
            pass
            #TODO support all field listing as default

class ListResourceItem(ResourceItem):
    form_class = ListForm
    
    def get_form_kwargs(self, **kwargs):
        kwargs = super(ListResourceItem, self).get_form_kwargs(**kwargs)
        form_kwargs = {'instance':kwargs.get('instance', None),
                       'resource':self.resource}
        return form_kwargs
