'''
Created on 07 Mar 2013

@author: michael
'''
from skyhigh.api import constants, models, utils, tasks
import json

def create_account(sftp_user):
    request_data = json.dumps({'username': sftp_user.username, 'password': sftp_user.password})
    request_type = constants.REQUEST_TYPE_CREATE_SFTP_ACCOUNT
    request = models.Request.objects.create(type=request_type,
                                  request_data=request_data)
    if request.status in [constants.REQUEST_STATUS_CREATED,
                       constants.REQUEST_STATUS_RETRY]:
        tasks.send_request.delay(request.pk, 'create_sftp_account')


def update_account(sftp_user):
    request_data = json.dumps({'username': sftp_user.username, 'password': sftp_user.password})
    request_type = constants.REQUEST_TYPE_UPDATE_SFTP_ACCOUNT
    request = models.Request.objects.create(type=request_type, 
                                  request_data=request_data)
    
    if request.status in [constants.REQUEST_STATUS_CREATED,
                       constants.REQUEST_STATUS_RETRY]:
        tasks.send_request.delay(request.pk, 'update_sftp_account')