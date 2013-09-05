'''
Created on 19 Nov 2012

@author: euan
'''
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site

from registration import signals
from registration.backends.default import DefaultBackend

from skyhigh import forms, models, user_actions

class SkyHighRegistrationBackend(DefaultBackend):
    
    def register(self, request, **kwargs):
        
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
            
        new_profile = models.SkyHighRegistrationProfile.objects.create_inactive_profile(site=site, request=request, send_email=True, **kwargs)
        
        signals.user_registered.send(sender=self.__class__,
                                     user=new_profile.user,
                                     request=request)

        user_actions.action_new_profile_registration(new_profile.user)


        return new_profile.user
    
    def get_form_class(self, request):
        return forms.SkyHighRegistrationForm