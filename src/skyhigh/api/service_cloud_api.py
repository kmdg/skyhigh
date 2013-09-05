'''
Created on 15 Jan 2013

@author: euan
'''
from celery.decorators import task

from django.conf import settings
from django.utils import timezone
from django.utils.html import strip_tags
from django.contrib.auth.models import User

from unobase.support import models as support_models

from skyhigh.api import models, constants, utils

from sforce.enterprise import SforceEnterpriseClient

def save_request(attrs, request_type, response):
    request_log_kwargs = {'action' : constants.REQUEST_ACTION_SEND}

    request = models.Request.objects.create(type=request_type,
        request_data=str(attrs), response_data=response)

    status = 'success' if response.success else 'error'

    if status == 'success':
        request_log_kwargs.update({'result' : constants.REQUEST_STATUS_COMPLETED})
        request.status = constants.REQUEST_STATUS_COMPLETED
        request.completed_timestamp = timezone.now()
    else:
        if request.send_count > request.retries:
            request_log_kwargs.update({'result' : constants.REQUEST_STATUS_FAILED})
            request.status = constants.REQUEST_STATUS_FAILED
        else:
            request_log_kwargs.update({'result' : constants.REQUEST_STATUS_RETRY})
            request.status = constants.REQUEST_STATUS_RETRY

    request.save()
    models.RequestLog.objects.create(request=request, **request_log_kwargs)
    
def login():
    h = SforceEnterpriseClient('%s/skyhigh/wsdl/skyhigh_salesforce_enterprise.wsdl.xml' % settings.STATIC_ROOT)
    h.login(settings.SERVICE_CLOUD_USERNAME, settings.SERVICE_CLOUD_PASSWORD, settings.SERVICE_CLOUD_SECURITY_TOKEN)
    
    return h

@task()
def sync_case(case_id):
    support_case = support_models.Case.objects.get(pk=case_id)
    user = support_case.created_by

    h = login()

    case = h.generateObject('Case')
    case.Status = support_case.get_status_display()
    case.Origin = support_case.get_origin_display()
    case.Type = support_case.get_type_display()
    case.Priority = support_case.get_priority_display()
    case.Reason = support_case.get_reason_display()
    case.Subject = support_case.title
    case.Description = strip_tags(support_case.content)

    result = h.query("SELECT Id FROM Contact WHERE Email='%s'" % user.email)
    if result.done and result.size:
        case.ContactId = result.records[0].Id
    else:
        contact = h.generateObject('Contact')
        contact.FirstName = user.profile.first_name
        contact.LastName = user.profile.last_name
        contact.Email = user.email
        result = h.create(contact)

        if result.success:
            case.ContactId = result.id

    response = h.create(case)

    save_request(case, constants.REQUEST_TYPE_CREATE_CASE, response)
    
@task()
def sync_new_profile_registration(user_id):
    user = User.objects.get(pk=user_id)
    
    h = login()
    
    lead = h.generateObject('Lead')
    
    result = h.query("SELECT Id FROM Lead WHERE Email='%s'" % user.email)
    if result.done and result.size:
        lead.Id = result.records[0].Id
    lead.Salutation = utils.not_null_str(user.profile.title)
    lead.FirstName = utils.not_null_str(user.first_name)
    lead.LastName = utils.not_null_str(user.last_name)
    lead.Email = utils.not_null_str(user.email)
    lead.Title = utils.not_null_str(user.profile.job_title)
    lead.Company = utils.not_null_str(user.profile.company)
    lead.Phone = utils.not_null_str(user.profile.phone_number)
    lead.Website = utils.not_null_str(user.profile.website)
    lead.Industry = utils.not_null_str(user.profile.get_industry_display())
    lead.NumberOfEmployees = utils.not_null_str(user.profile.get_num_employees_display())
    lead.Rating = user.profile.maturation_score
    lead.LeadSource = 'Site Registration'

    response = h.upsert('Id', lead)

    save_request(lead, constants.REQUEST_TYPE_CREATE_PROFILE, response)
    
@task()
def sync_profile_update(user_id):
    user = User.objects.get(pk=user_id)
    
    h = login()
    
    lead = h.generateObject('Lead')
    
    result = h.query("SELECT Id FROM Lead WHERE Email='%s'" % user.email)
    if result.done and result.size:
        lead.Id = result.records[0].Id
    lead.Salutation = utils.not_null_str(user.profile.title)
    lead.FirstName = utils.not_null_str(user.first_name)
    lead.LastName = utils.not_null_str(user.last_name)
    lead.Email = utils.not_null_str(user.email)
    lead.Title = utils.not_null_str(user.profile.job_title)
    lead.Company = utils.not_null_str(user.profile.company)
    lead.Phone = utils.not_null_str(user.profile.phone_number)
    lead.Website = utils.not_null_str(user.profile.website)
    lead.Industry = utils.not_null_str(user.profile.get_industry_display())
    lead.NumberOfEmployees = utils.not_null_str(user.profile.get_num_employees_display())
    lead.Rating = user.profile.maturation_score
    lead.LeadSource = 'Profile Update'

    response = h.upsert('Id', lead)

    save_request(lead, constants.REQUEST_TYPE_UPDATE_PROFILE, response)
    
@task()
def sync_contact_message_sent(user_id):
    user = User.objects.get(pk=user_id)
    
    h = login()
    
    lead = h.generateObject('Lead')
    
    result = h.query("SELECT Id FROM Lead WHERE Email='%s'" % user.email)
    if result.done and result.size:
        lead.Id = result.records[0].Id
    lead.Salutation = utils.not_null_str(user.profile.title)
    lead.FirstName = utils.not_null_str(user.first_name)
    lead.LastName = utils.not_null_str(user.last_name)
    lead.Email = utils.not_null_str(user.email)
    lead.Title = utils.not_null_str(user.profile.job_title)
    lead.Company = utils.not_null_str(user.profile.company)
    lead.Rating = user.profile.maturation_score
    lead.LeadSource = 'Contact Message'

    response = h.upsert('Id', lead)

    save_request(lead, constants.REQUEST_TYPE_CONTACT_MESSAGE_SENT, response)
    
@task()
def sync_product_evaluation_request(user_id):
    user = User.objects.get(pk=user_id)
    
    h = login()
    
    lead = h.generateObject('Lead')
    
    result = h.query("SELECT Id FROM Lead WHERE Email='%s'" % user.email)
    if result.done and result.size:
        lead.Id = result.records[0].Id
    lead.Salutation = utils.not_null_str(user.profile.title)
    lead.FirstName = utils.not_null_str(user.first_name)
    lead.LastName = utils.not_null_str(user.last_name)
    lead.Email = utils.not_null_str(user.email)
    lead.Title = utils.not_null_str(user.profile.job_title)
    lead.Company = utils.not_null_str(user.profile.company)
    lead.Rating = user.profile.maturation_score
    lead.LeadSource = 'Product Evaluation Request'

    response = h.upsert('Id', lead)

    save_request(lead, constants.REQUEST_TYPE_EVALUATION_REQUEST, response)
    
@task()
def sync_partnership_request(user_id):
    user = User.objects.get(pk=user_id)
    
    h = login()
    
    lead = h.generateObject('Lead')
    
    result = h.query("SELECT Id FROM Lead WHERE Email='%s'" % user.email)
    if result.done and result.size:
        lead.Id = result.records[0].Id
    lead.Salutation = utils.not_null_str(user.profile.title)
    lead.FirstName = utils.not_null_str(user.first_name)
    lead.LastName = utils.not_null_str(user.last_name)
    lead.Email = utils.not_null_str(user.email)
    lead.Title = utils.not_null_str(user.profile.job_title)
    lead.Company = utils.not_null_str(user.profile.company)
    lead.Rating = user.profile.maturation_score
    lead.LeadSource = 'Partnership Request'

    response = h.upsert('Id', lead)

    save_request(lead, constants.REQUEST_TYPE_CONTACT_MESSAGE_SENT, response)