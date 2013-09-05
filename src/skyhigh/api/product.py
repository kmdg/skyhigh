'''
Created on 15 Jan 2013

@author: euan
'''
from skyhigh.api import constants, models, utils, tasks

def create_evaluation_account(user):
    request_obj = user.profile
    request_fields = ('user_ptr', 'first_name','last_name', 'email', 'company', 'job_title',
                      'phone_number', 'mobile_number', 'address', 'city', 
                      'zip_postal_code', 'state_province', 'country', 'company', 
                      'timezone')
    relations = ('user_ptr', 'state_province', 'country')
    request_data = utils.get_dict(request_obj, request_fields, relations)
    request_type = constants.REQUEST_TYPE_CREATE_EVALUATION_ACCOUNT
    request = models.Request.objects.create(type=request_type,
                                  request_data=request_data)
    if request.status in [constants.REQUEST_STATUS_CREATED,
                       constants.REQUEST_STATUS_RETRY]:
        tasks.send_request.delay(request.pk, 'create_evaluation_account')


def update_profile(user):
    request_obj = user.profile
    request_fields = ('user_ptr', 'first_name','last_name', 'email', 'company', 'job_title',
                      'phone_number', 'mobile_number', 'address', 'city', 
                      'zip_postal_code', 'state_province', 'country', 'company', 
                      'timezone')
    relations = ('user_ptr', 'state_province', 'country')
    request_data = utils.get_dict(request_obj, request_fields, relations)
    request_type = constants.REQUEST_TYPE_UPDATE_PROFILE
    request = models.Request.objects.create(type=request_type, 
                                  request_data=request_data)
    
    if request.status in [constants.REQUEST_STATUS_CREATED,
                       constants.REQUEST_STATUS_RETRY]:
        tasks.send_request.delay(request.pk, 'update_profile')