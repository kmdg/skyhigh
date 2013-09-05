__author__ = 'michael'

from django import template

from skyhigh import forms

register = template.Library()

@register.inclusion_tag('skyhigh/inclusion_tags/newsletter_signup.html', takes_context=True)
def newsletter_signup(context):
    request = context['request']
    return {'form' : forms.NewsletterSignupForm(initial={'user': request.user}),
            'user': request.user,
            'secure': 'secure' in request.path
            }