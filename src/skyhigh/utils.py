'''
Created on 03 Jan 2013

@author: euan
'''
import json
import hashlib

from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.template import Context, Template
from django import http
from django.contrib.sites.models import Site

import HTMLParser

from unobase.email_tracking import models as email_tracker_models

def send_mail(template_name, context, subject, text_content, from_address, to_addresses, attachments=None, html_content=None, user=None):
    """
    Sends an email containing both text(provided) and html(produced from
    povided template name and context) content as well as provided
    attachments to provided to_addresses from provided from_address.
    """
    if settings.EMAIL_ENABLED:
        # Build message with text_message as default content.
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            from_address,
            to_addresses,
        )
    
        # Set html content from message for HTML capable clients.
        context.update({
            'STATIC_URL': settings.STATIC_URL,
            'site' : Site.objects.get_current()
        })
    
        if template_name is not None:
            html_content = render_to_string(
                template_name,
                context,
            )
    
        if html_content is not None:
            msg.attach_alternative(html_content, "text/html")
    
        # Add attachments.
        if attachments:
            for attachment in attachments:
                if attachment:
                    msg.attach(attachment.name, attachment.read())
    
        # Send message.
        connection = get_connection()
        connection.send_messages([msg, ])
    
        if user is not None:
            email_tracker_models.OutboundEmail.objects.create(user=user, subject=subject, message=html_content or text_content)

def respond_with_json(response_params):
    response = http.HttpResponse(json.dumps(response_params, indent=4))
    response['mimetype'] = 'application/javascript'
    response['Access-Control-Allow-Origin'] = '*'
    return response

def get_email_context(user):
    return {'user' : user,
            'app_name': settings.APP_NAME}

def get_email_subject(template_name, ctx_dict):
    return ''.join(render_to_string(template_name,
        ctx_dict).splitlines())

def get_email_text_content(template_name, ctx_dict):
    return render_to_string(template_name,
        ctx_dict)
    
def get_configurable_email_context(user):
    return {'user' : user,
            'app_name': settings.APP_NAME}

def get_configurable_email_subject(configurable_email, ctx_dict):
    t = Template(configurable_email.subject)
    c = Context(ctx_dict)
    
    email_content = t.render(c)
    
    return ''.join(render_to_string('skyhigh/configurable_email/base_subject.txt',
        {'email_content': email_content}).splitlines())

def get_configurable_email_text_content(configurable_email, ctx_dict):
    t = Template(configurable_email.plaintext_content)
    c = Context(ctx_dict)
    
    email_content = t.render(c)
    
    ctx_dict.update({'email_content': email_content})
    
    return render_to_string('skyhigh/configurable_email/base.txt',
        ctx_dict)
    
def get_configurable_email_html_content(configurable_email, ctx_dict):
    t = Template(configurable_email.content)
    c = Context(ctx_dict)
    
    email_content = HTMLParser.HTMLParser().unescape(t.render(c))
    
    ctx_dict.update({'email_content': email_content,
                     'STATIC_URL': settings.STATIC_URL,})
    
    return render_to_string('skyhigh/configurable_email/base.html',
        ctx_dict)
    
def get_token_for_user(user):
    return hashlib.md5(user.email + settings.SECRET_KEY).hexdigest()