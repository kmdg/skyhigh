'''
Created on 17 Jan 2013

@author: euan
'''
from django import template
from django.utils import timezone

from skyhigh import constants, models as skyhigh_models

from unobase import constants as unobase_constants
from unobase.blog import models as blog_models

register = template.Library()

@register.inclusion_tag('skyhigh/inclusion_tags/recent_blog_posts.html')
def recent_blog_posts(amount=3):
    return {'objects' : blog_models.BlogEntry.objects.filter(state=unobase_constants.STATE_PUBLISHED).order_by('-created')[0:amount] }

@register.inclusion_tag('skyhigh/inclusion_tags/upcoming_events.html')
def upcoming_events(amount=3):
    return {'objects' : skyhigh_models.Event.objects.filter(state=unobase_constants.STATE_PUBLISHED,
                                                            start_date__gte=timezone.now()).order_by('-created')[0:amount] }

@register.inclusion_tag('skyhigh/inclusion_tags/recent_media_coverage.html')
def recent_media_coverage(amount=3):
    return {'objects' : skyhigh_models.MediaCoverage.objects.filter(state=unobase_constants.STATE_PUBLISHED).order_by('-created')[0:amount] }

@register.inclusion_tag('skyhigh/inclusion_tags/recent_press_releases.html')
def recent_press_releases(amount=3):
    return {'objects' : skyhigh_models.PressRelease.objects.filter(state=unobase_constants.STATE_PUBLISHED).order_by('-created')[0:amount] }

@register.inclusion_tag('skyhigh/inclusion_tags/latest_unread_messages.html')
def latest_unread_messages(amount=3):
    print skyhigh_models.ContactMessage.objects.filter(status=constants.CONTACT_MESSAGE_STATUS_UNREAD).order_by('-sent_date')[0:amount]
    return {'objects' : skyhigh_models.ContactMessage.objects.filter(status=constants.CONTACT_MESSAGE_STATUS_UNREAD).order_by('-sent_date')[0:amount] }