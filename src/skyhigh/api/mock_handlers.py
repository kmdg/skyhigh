'''
Created on 15 Jan 2013

@author: euan
'''
from django.http import HttpResponse
from django.views import generic as generic_views

class PostSuccessHandler(generic_views.View):
    
    def post(self, request, *args, **kwargs):
        print request.body
        return HttpResponse('Success')

class PostFailureHandler(generic_views.View):

    def post(self, request, *args, **kwargs):
        print request.body
        return HttpResponse('Failure')