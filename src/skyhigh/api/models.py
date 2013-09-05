'''
Created on 15 Jan 2013

@author: euan
'''
import json
import uuid

from django.db import models
from skyhigh.api import exceptions, constants, utils

class Destination(models.Model):
    """
    Where to send stuff.
    """
    title = models.CharField(max_length=32)
    url = models.URLField()
    username = models.CharField(max_length=200, blank=True, null=True)
    password = models.CharField(max_length=200, blank=True, null=True)
    
    def __unicode__(self):
        return u'%s' % self.title
    
class Service(models.Model):
    """
    Where to send stuff of a certain type and how many times to retry.
    """
    type = models.PositiveSmallIntegerField(unique=True,
                                            choices=constants.REQUEST_TYPE_CHOICES)
    destination = models.ForeignKey(Destination)
    retries = models.PositiveSmallIntegerField(default=3)
    
    def __unicode__(self):
        return u'%s' % self.get_type_display()

class Request(models.Model):
    """
    The actual stuff being sent.
    """
    uuid = models.CharField(max_length=64, editable=False)
    type = models.PositiveSmallIntegerField(choices=constants.REQUEST_TYPE_CHOICES)
    url = models.URLField(blank=True, null=True)
    retries = models.PositiveSmallIntegerField(default=3)
    request_data = models.TextField()
    response_data = models.TextField(blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=constants.REQUEST_STATUS_CHOICES,
                                              default=constants.REQUEST_STATUS_CREATED)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    completed_timestamp = models.DateTimeField(blank=True, null=True)
    
    def __unicode__(self):
        return u'%s' % self.url
    
    @property
    def send_count(self):
        return RequestLog.objects.filter(request=self,
                                         action=constants.REQUEST_ACTION_SEND).count()
    
    def save(self, *args, **kwargs):
        try:
            service = Service.objects.get(type=self.type)
            self.url = service.destination.url
            
            if not self.uuid:
                self.uuid = uuid.uuid4()
                while Request.objects.filter(uuid=self.uuid).count() > 1:
                    self.uuid = uuid.uuid4()
            
            super(Request, self).save(*args, **kwargs)
            
        except Service.DoesNotExist:
            raise exceptions.APIConfigurationException('Service for type %s does not exist.' % self.get_type_display())

def post_save_request(sender, instance, created, **kwargs):
    if created:
        RequestLog.objects.create(request=instance,
                                  action=constants.REQUEST_ACTION_CREATE,
                                  result=constants.REQUEST_STATUS_CREATED)

models.signals.post_save.connect(post_save_request, sender=Request)

class RequestLog(models.Model):
    """
    A log of what happened.
    """
    request = models.ForeignKey(Request)
    action = models.PositiveSmallIntegerField(choices=constants.REQUEST_ACTION_CHOICES)
    result = models.PositiveSmallIntegerField(choices=constants.REQUEST_STATUS_CHOICES)
    narration = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    