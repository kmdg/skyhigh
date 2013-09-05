'''
Created on 18 Mar 2013

@author: michael
'''
__author__ = 'michael'

from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

from celery.decorators import task
from skyhigh.api import constants, utils, models

import json

def save_request(attrs, request_type, response):
    request_log_kwargs = {'action' : constants.REQUEST_ACTION_SEND}

    request = models.Request.objects.create(type=request_type,
        request_data=str(attrs), response_data=response)

    status = response.syncStatus.status

    if status == 'CREATED' or status == 'UPDATED':
        request_log_kwargs.update({'result' : constants.REQUEST_STATUS_COMPLETED})
        request.status = constants.REQUEST_STATUS_COMPLETED
        request.completed_timestamp = timezone.now()
        request.save()
    else:
        if request.send_count > request.retries:
            request_log_kwargs.update({'result' : constants.REQUEST_STATUS_FAILED})
            request.status = constants.REQUEST_STATUS_FAILED
            request.save()
        else:
            request_log_kwargs.update({'result' : constants.REQUEST_STATUS_RETRY})
            request.status = constants.REQUEST_STATUS_RETRY
            request.save()
            models.RequestLog.objects.create(request=request, **request_log_kwargs)
            raise Exception('Retry send')
            
    models.RequestLog.objects.create(request=request, **request_log_kwargs)

@task(default_retry_delay=10 * 60)
def get_registrant(user_id):
    try:
        user = User.objects.get(pk=user_id)
        
        url = settings.GO_TO_WEBINAR_REST_SERVICE_ENDPOINT % {'webinar_key': 'webinar1'}
        registrant_key = 'registrantkey1'
    
        response = utils.do_post(url='%s/registrants/%s' % (url, registrant_key),
                                     content_type='application/json',
                                     oauth_token='120000009')
    
        save_request(constants.REQUEST_TYPE_CREATE_PROFILE, response)
    except Exception, exc:
        raise get_registrant.retry(exc=exc)