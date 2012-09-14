from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json
from django import http

from common import MediaType, BUILTIN_MEDIA_TYPES

class JSON(MediaType):
    def convert_item(self, item):
        return self.get_form_instance_values(item.form)
    
    def get_payload(self, form_link, meta=None):
        resource_item = form_link.resource_item
        
        items = [self.convert_item(item) for item in resource_item.get_resource_items()]
        
        #TODO if not collection resource item
        #if instance:
        #    return items[0]
        return items
    
    def serialize(self, content_type, link, meta=None):
        if self.detect_redirect(link):
            return self.handle_redirect(link)
        data = self.get_payload(link, meta=meta)
        content = json.dumps(data, cls=DjangoJSONEncoder)
        return http.HttpResponse(content, content_type)
    
    def deserialize(self):
        if hasattr(self.request, 'body'):
            payload = self.request.body
        else:
            payload = self.request.raw_post_data
        data = json.loads(payload)
        return {'data':data,
                'files':self.request.FILES,}

BUILTIN_MEDIA_TYPES['application/json'] = JSON

class JSONP(JSON):
    def get_jsonp_callback(self):
        #TODO make configurable
        return self.view.request.GET['callback']
    
    def serialize(self, content_type, link, meta=None):
        data = self.get_payload(link, meta=meta)
        content = json.dumps(data, cls=DjangoJSONEncoder)
        callback = self.get_jsonp_callback()
        return http.HttpResponse(u'%s(%s)' % (callback, content), content_type)

BUILTIN_MEDIA_TYPES['text/javascript'] = JSONP

