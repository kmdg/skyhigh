__author__ = 'michael'
from celery.decorators import task
from skyhigh.api import exceptions, constants, utils, models
from django.utils import timezone
import json

@task(default_retry_delay=10 * 60)
def send_request(request_id, request_type):
    try:
        request_log_kwargs = {'action' : constants.REQUEST_ACTION_SEND}
        request = models.Request.objects.get(pk=request_id)
    
        data = {'request_type' : request_type,
                'uuid' : str(request.uuid),
                'user_data' : json.loads(request.request_data)
        }
        
        service = models.Service.objects.get(type=request.type)
        
        response = utils.do_post(url=request.url, body=json.dumps(data), 
                                     content_type='application/json', trusted_ssl=True,
                                     username=service.destination.username or None, password=service.destination.password or None)
        
        request.response_data = response
        
        response_json = json.loads(response)
    
        if response_json['status'] == 'SUCCESS':
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
    except Exception, exc:
        raise send_request.retry(exc=exc)