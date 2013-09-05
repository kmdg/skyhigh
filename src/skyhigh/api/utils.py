'''
Created on 15 Jan 2013

@author: euan
'''
import pycurl
import types

from cStringIO import StringIO
from django.core.serializers import serialize
from django.utils.encoding import smart_unicode

PYCURL_VERBOSE = 1
PYCURL_CONNECT_TIMEOUT = 5

def get_dict(obj, fields=None, relations=None):
    obj_dict = serialize('json', obj, fields_only=True, relations=relations, fields=fields)

    return obj_dict

def do_post(url, parameters=None, body=None, username=None, 
            password=None, content_type=None, user_agent='CurlUtil',
            verbose=PYCURL_VERBOSE, timeout=PYCURL_CONNECT_TIMEOUT, oauth_token=None, trusted_ssl=False):
    
    request = pycurl.Curl()
    response = StringIO()
    
    request.setopt(pycurl.VERBOSE, verbose)
    request.setopt(pycurl.POST, 1)
    request.setopt(pycurl.URL, str(url))
    request.setopt(pycurl.CONNECTTIMEOUT, timeout)
    request.setopt(pycurl.HTTPHEADER, ['User-Agent: %s' % user_agent])
    request.setopt(pycurl.WRITEFUNCTION, response.write)
    
    if trusted_ssl:
        request.setopt(pycurl.SSL_VERIFYPEER, 0)
        request.setopt(pycurl.SSL_VERIFYHOST, 0)
    
    if username is not None and password is not None:
        request.setopt(pycurl.USERPWD, str('%s:%s' % (username, password)))
    if parameters:
        request.setopt(pycurl.HTTPPOST, parameters)
    if body:
        request.setopt(pycurl.POSTFIELDS, str(body))
    if content_type:
        request.setopt(pycurl.HTTPHEADER, ['Content-type: %s' % content_type])
    if oauth_token:
        request.setopt(pycurl.HTTPHEADER, ['Authorization: OAuth %s' % oauth_token])
    
    request.perform()
    
    return response.getvalue()

def ensure_unicode(the_string):
    """
    Just checking...
    """
    if not type(the_string) == types.UnicodeType:
    #        the_string = unicode(str(the_string))
        the_string = smart_unicode(the_string)

    return smart_unicode(the_string)

def not_null_str(obj):
    """
    Ensures that the returned string is not null
    """
    if obj == None:
        return ''
    else:
        return ensure_unicode(obj)