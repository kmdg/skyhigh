'''
Created on 15 Jan 2013

@author: euan
'''
from django.contrib import admin

from skyhigh.api import models

admin.site.register(models.Destination)
admin.site.register(models.Service)
admin.site.register(models.Request)
admin.site.register(models.RequestLog)