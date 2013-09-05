'''
Created on 15 Jan 2013

@author: euan
'''
from celery.decorators import task

from django.utils import timezone
from django.contrib.auth.models import User

from marketo import client as marketo_client

from skyhigh.api import models, utils, constants

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
def sync_new_profile_registration(user_id):
    try:
        user = User.objects.get(pk=user_id)
        attrs = {'Salutation': utils.not_null_str(user.profile.title),
                 'FirstName': utils.not_null_str(user.first_name),
                 'LastName': utils.not_null_str(user.last_name),
                 'Email': utils.not_null_str(user.email),
                 'Title': utils.not_null_str(user.profile.job_title),
                 'Company': utils.not_null_str(user.profile.company),
                 'Phone': utils.not_null_str(user.profile.phone_number),
                 'PostalCode': utils.not_null_str(user.profile.zip_postal_code),
                 'LeadScore': user.profile.maturation_score,
                 'LeadSource': 'Site Registration',
                 'RecordTypeId': '01290000000gFXXAA2',
                 #'Search_String__c': utils.not_null_str(user.profile.search_string),
                 #'Search_Engine__c': utils.not_null_str(user.profile.search_engine),
                 #'Pay_Per_Click_Keyword__c': utils.not_null_str(user.profile.pay_per_click_keyword)
                 }
    
        response = marketo_client.sync_lead_by_email(user.email, attrs)
    
        save_request(attrs, constants.REQUEST_TYPE_CREATE_PROFILE, response)
    except Exception, exc:
        raise sync_new_profile_registration.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def sync_profile_update(user_id):
    try:
        user = User.objects.get(pk=user_id)
        attrs = {'Salutation': utils.not_null_str(user.profile.title),
                 'FirstName': utils.not_null_str(user.first_name),
                 'LastName': utils.not_null_str(user.last_name),
                 'Email': utils.not_null_str(user.email),
                 'Title': utils.not_null_str(user.profile.job_title),
                 'Company': utils.not_null_str(user.profile.company),
                 'Phone': utils.not_null_str(user.profile.phone_number),
                 'PostalCode': utils.not_null_str(user.profile.zip_postal_code),
                 'Industry': utils.not_null_str(user.profile.get_industry_display()),
                 'NumberOfEmployees': utils.not_null_str(user.profile.get_num_employees_display()),
                 'Website': utils.not_null_str(user.profile.website),
                 'LeadScore': user.profile.maturation_score,
                 'LeadSource': 'Profile Update',
                 'How_did_you_hear_about_us__c': utils.not_null_str(user.profile.get_heard_about_from_display()),
                 'Requests_for_Comments__c': utils.not_null_str(user.profile.requests_or_comments),
                 #'Search_String__c': utils.not_null_str(user.profile.search_string),
                 #'Search_Engine__c': utils.not_null_str(user.profile.search_engine),
                 #'Pay_Per_Click_Keyword__c': utils.not_null_str(user.profile.pay_per_click_keyword)
                 }
        
        if user.profile.is_partner:
            attrs.update({
                 'Number_of_Branches__c': user.profile.partnership.num_branches,
                 'Branch_Offices_City_State__c': utils.not_null_str(user.profile.partnership.branch_offices),
                 'Countries_Where_SH_will_be_Sold__c': utils.not_null_str(user.profile.partnership.countries_requesting_to_sell_in),
                 'States_Where_SH_will_be_Sold__c': utils.not_null_str(user.profile.partnership.us_states_requesting_to_sell_in),
                 'Years_in_Business__c':  user.profile.partnership.years_in_business,
                 'Number_of_Sales_Reps__c': user.profile.partnership.num_sales_reps,
                 'Number_of_Systems_Engineers__c': user.profile.partnership.num_systems_engineers,
                 'Number_of_Technical_Support_Staff__c': user.profile.partnership.num_technical_support_staff,
                 'Business_Type__c': utils.not_null_str(user.profile.partnership.get_business_type_display()),
                 'Preferred_Distributor__c': utils.not_null_str(user.profile.partnership.preferred_distributor),
                 'Target_Vertical_Focus__c': utils.not_null_str(', '.join([vf.vertical_focus for vf in user.profile.partnership.target_vertical_focus.all()])),
                 'Resell_to_US_Fed_Gov__c': utils.not_null_str(user.profile.partnership.get_resell_to_usa_federal_sectors_display()),
                 'Type_of_Support__c': utils.not_null_str(user.profile.partnership.get_offer_own_support_display()),
                 'Manufacturer_s_Sold__c': utils.not_null_str(user.profile.partnership.manufacturers_selling),
                 'Leading_Competitors__c': utils.not_null_str(user.profile.partnership.leading_competitors),
                 'Additional_Comments__c': utils.not_null_str(user.profile.partnership.additional_comments),
                 'Partner_Representative__c': utils.not_null_str(user.profile.partnership.representitive),
                 'Partner_VAT_GST_TAX_ID_Numbers__c': '%s/%s/%s' % (user.profile.partnership.vat_number, user.profile.partnership.gst_number, user.profile.partnership.tax_id_number),
                 'D_B_Number__c': utils.not_null_str(user.profile.partnership.d_and_b_number)
            })
    
        response = marketo_client.sync_lead_by_email(user.email, attrs)
    
        save_request(attrs, constants.REQUEST_TYPE_UPDATE_PROFILE, response)
    except Exception, exc:
        raise sync_profile_update.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def sync_contact_message_sent(user_id):
    try:
        user = User.objects.get(pk=user_id)
        attrs = {'Salutation': utils.not_null_str(user.profile.title),
                 'FirstName': utils.not_null_str(user.first_name),
                 'LastName': utils.not_null_str(user.last_name),
                 'Email': utils.not_null_str(user.email),
                 'Title': utils.not_null_str(user.profile.job_title),
                 'Company': utils.not_null_str(user.profile.company),
                 'LeadScore': user.profile.maturation_score,
                 'LeadSource': 'Contact Message',
                 'RecordTypeId': '01290000000gFjJAAU'}
    
        response = marketo_client.sync_lead_by_email(user.email, attrs)
    
        save_request(attrs, constants.REQUEST_TYPE_CONTACT_MESSAGE_SENT, response)
    except Exception, exc:
        raise sync_contact_message_sent.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def sync_product_evaluation_request(user_id):
    try:
        user = User.objects.get(pk=user_id)
        attrs = {'Salutation': utils.not_null_str(user.profile.title),
                 'FirstName': utils.not_null_str(user.first_name),
                 'LastName': utils.not_null_str(user.last_name),
                 'Email': utils.not_null_str(user.email),
                 'Title': utils.not_null_str(user.profile.job_title),
                 'Company': utils.not_null_str(user.profile.company),
                 'LeadScore': user.profile.maturation_score,
                 'LeadSource': 'Evaluation Request',
                 'Phone': utils.not_null_str(user.profile.phone_number),
                 'PostalCode': utils.not_null_str(user.profile.zip_postal_code),
                 'Requests_for_Comments__c': utils.not_null_str(user.profile.requests_or_comments),
                 'RecordTypeId': '01290000000gFXSAA2',
                 #'Search_String__c': utils.not_null_str(user.profile.search_string),
                 #'Search_Engine__c': utils.not_null_str(user.profile.search_engine),
                 #'Pay_Per_Click_Keyword__c': utils.not_null_str(user.profile.pay_per_click_keyword)
                 }
    
        response = marketo_client.sync_lead_by_email(user.email, attrs)
    
        save_request(attrs, constants.REQUEST_TYPE_EVALUATION_REQUEST, response)
    except Exception, exc:
        raise sync_product_evaluation_request.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def sync_partnership_request(user_id):
    try:
        user = User.objects.get(pk=user_id)
        record_type_id = '01290000000gJFGAA2'
        source = 'Partnership Request'
        
        if user.profile.is_cloud_service_provider:
            record_type_id = '01290000000gL48AAE'
            source = 'CSP Partnership Request'
        elif user.profile.is_channel_partner:
            record_type_id = '01290000000gJFGAA2'
            source = 'Channel Partnership Request'
        elif user.profile.is_technical_partner:
            record_type_id = '01290000000gL43AAE'
            source = 'Technical Partnership Request'
        
        attrs = {'Salutation': utils.not_null_str(user.profile.title),
                 'FirstName': utils.not_null_str(user.first_name),
                 'LastName': utils.not_null_str(user.last_name),
                 'Email': utils.not_null_str(user.email),
                 'Title': utils.not_null_str(user.profile.job_title),
                 'Company': utils.not_null_str(user.profile.company),
                 'LeadScore': user.profile.maturation_score,
                 'LeadSource': source,
                 'Number_of_Branches__c': user.profile.partnership.num_branches,
                 'Branch_Offices_City_State__c': utils.not_null_str(user.profile.partnership.branch_offices),
                 'Countries_Where_SH_will_be_Sold__c': utils.not_null_str(user.profile.partnership.countries_requesting_to_sell_in),
                 'States_Where_SH_will_be_Sold__c': utils.not_null_str(user.profile.partnership.us_states_requesting_to_sell_in),
                 'Years_in_Business__c':  user.profile.partnership.years_in_business,
                 'Number_of_Sales_Reps__c': user.profile.partnership.num_sales_reps,
                 'Number_of_Systems_Engineers__c': user.profile.partnership.num_systems_engineers,
                 'Number_of_Technical_Support_Staff__c': user.profile.partnership.num_technical_support_staff,
                 'Business_Type__c': utils.not_null_str(user.profile.partnership.get_business_type_display()),
                 'Preferred_Distributor__c': utils.not_null_str(user.profile.partnership.preferred_distributor),
                 'Target_Vertical_Focus__c': utils.not_null_str(', '.join([vf.vertical_focus for vf in user.profile.partnership.target_vertical_focus.all()])),
                 'Resell_to_US_Fed_Gov__c': utils.not_null_str(user.profile.partnership.get_resell_to_usa_federal_sectors_display()),
                 'Type_of_Support__c': utils.not_null_str(user.profile.partnership.get_offer_own_support_display()),
                 'Manufacturer_s_Sold__c': utils.not_null_str(user.profile.partnership.manufacturers_selling),
                 'Leading_Competitors__c': utils.not_null_str(user.profile.partnership.leading_competitors),
                 'Additional_Comments__c': utils.not_null_str(user.profile.partnership.additional_comments),
                 'Partner_Representative__c': utils.not_null_str(user.profile.partnership.representitive),
                 'Partner_VAT_GST_TAX_ID_Numbers__c': '%s/%s/%s' % (user.profile.partnership.vat_number, user.profile.partnership.gst_number, user.profile.partnership.tax_id_number),
                 'D_B_Number__c': utils.not_null_str(user.profile.partnership.d_and_b_number),
                 'Phone': utils.not_null_str(user.profile.phone_number),
                 'PostalCode': utils.not_null_str(user.profile.zip_postal_code),
                 'Requests_for_Comments__c': utils.not_null_str(user.profile.requests_or_comments),
                 'RecordTypeId': record_type_id,
                 #'Search_String__c': utils.not_null_str(user.profile.search_string),
                 #'Search_Engine__c': utils.not_null_str(user.profile.search_engine),
                 #'Pay_Per_Click_Keyword__c': utils.not_null_str(user.profile.pay_per_click_keyword)
                 }
    
        response = marketo_client.sync_lead_by_email(user.email, attrs)
    
        save_request(attrs, constants.REQUEST_TYPE_PARTNERSHIP_REQUEST, response)
    except Exception, exc:
        raise sync_partnership_request.retry(exc=exc)
    
@task(default_retry_delay=10 * 60)
def sync_deal_request_submitted(user_id):
    try:
        user = User.objects.get(pk=user_id)
        attrs = {'Salutation': utils.not_null_str(user.profile.title),
                 'FirstName': utils.not_null_str(user.first_name),
                 'LastName': utils.not_null_str(user.last_name),
                 'Email': utils.not_null_str(user.email),
                 'Title': utils.not_null_str(user.profile.job_title),
                 'Company': utils.not_null_str(user.profile.company),
                 'LeadScore': user.profile.maturation_score,
                 'LeadSource': 'Deal Request',
                 'Number_of_Branches__c': user.profile.partnership.num_branches,
                 'Branch_Offices_City_State__c': utils.not_null_str(user.profile.partnership.branch_offices),
                 'Countries_Where_SH_will_be_Sold__c': utils.not_null_str(user.profile.partnership.countries_requesting_to_sell_in),
                 'States_Where_SH_will_be_Sold__c': utils.not_null_str(user.profile.partnership.us_states_requesting_to_sell_in),
                 'Years_in_Business__c':  user.profile.partnership.years_in_business,
                 'Number_of_Sales_Reps__c': user.profile.partnership.num_sales_reps,
                 'Number_of_Systems_Engineers__c': user.profile.partnership.num_systems_engineers,
                 'Number_of_Technical_Support_Staff__c': user.profile.partnership.num_technical_support_staff,
                 'Business_Type__c': utils.not_null_str(user.profile.partnership.get_business_type_display()),
                 'Preferred_Distributor__c': utils.not_null_str(user.profile.partnership.preferred_distributor),
                 'Target_Vertical_Focus__c': utils.not_null_str(', '.join([vf.vertical_focus for vf in user.profile.partnership.target_vertical_focus.all()])),
                 'Resell_to_US_Fed_Gov__c': utils.not_null_str(user.profile.partnership.get_resell_to_usa_federal_sectors_display()),
                 'Type_of_Support__c': utils.not_null_str(user.profile.partnership.get_offer_own_support_display()),
                 'Manufacturer_s_Sold__c': utils.not_null_str(user.profile.partnership.manufacturers_selling),
                 'Leading_Competitors__c': utils.not_null_str(user.profile.partnership.leading_competitors),
                 'Additional_Comments__c': utils.not_null_str(user.profile.partnership.additional_comments),
                 'Partner_Representative__c': utils.not_null_str(user.profile.partnership.representitive),
                 'Partner_VAT_GST_TAX_ID_Numbers__c': '%s/%s/%s' % (user.profile.partnership.vat_number, user.profile.partnership.gst_number, user.profile.partnership.tax_id_number),
                 'D_B_Number__c': utils.not_null_str(user.profile.partnership.d_and_b_number),
                 'Phone': utils.not_null_str(user.profile.phone_number),
                 'PostalCode': utils.not_null_str(user.profile.zip_postal_code),
                 'Requests_for_Comments__c': utils.not_null_str(user.profile.requests_or_comments),
                 'RecordTypeId': '01290000000gFY1AAM',
                 #'Search_String__c': utils.not_null_str(user.profile.search_string),
                 #'Search_Engine__c': utils.not_null_str(user.profile.search_engine),
                 #'Pay_Per_Click_Keyword__c': utils.not_null_str(user.profile.pay_per_click_keyword)
                 }
    
        response = marketo_client.sync_lead_by_email(user.email, attrs)
    
        save_request(attrs, constants.REQUEST_TYPE_DEAL_REQUEST, response)
    except Exception, exc:
        raise sync_deal_request_submitted.retry(exc=exc)