'''
Created on 15 Jan 2013

@author: euan
'''

REQUEST_TYPE_EVALUATION_REQUEST = 0
REQUEST_TYPE_CREATE_PROFILE = 1
REQUEST_TYPE_UPDATE_PROFILE = 2
REQUEST_TYPE_VERIFY_PASSWORD_STRENGTH = 3
REQUEST_TYPE_CONTACT_MESSAGE_SENT = 4
REQUEST_TYPE_PARTNERSHIP_REQUEST = 5
REQUEST_TYPE_CREATE_CASE = 6
REQUEST_TYPE_DEAL_REQUEST = 7
REQUEST_TYPE_CREATE_EVALUATION_ACCOUNT = 8
REQUEST_TYPE_CREATE_SFTP_ACCOUNT = 9
REQUEST_TYPE_UPDATE_SFTP_ACCOUNT = 10

REQUEST_TYPE_CHOICES = ((REQUEST_TYPE_EVALUATION_REQUEST, 'Evaluation Request'),
                        (REQUEST_TYPE_CREATE_PROFILE, 'Create Profile'),
                        (REQUEST_TYPE_UPDATE_PROFILE, 'Update Profile'),
                        (REQUEST_TYPE_VERIFY_PASSWORD_STRENGTH, 'Verify Password Strength'),
                        (REQUEST_TYPE_CONTACT_MESSAGE_SENT, 'Contact Message Sent'),
                        (REQUEST_TYPE_PARTNERSHIP_REQUEST, 'Partnership Request'),
                        (REQUEST_TYPE_CREATE_CASE, 'Case Create'),
                        (REQUEST_TYPE_DEAL_REQUEST, 'Deal Request'),
                        (REQUEST_TYPE_CREATE_EVALUATION_ACCOUNT, 'Create Evaluation Account'),
                        (REQUEST_TYPE_CREATE_SFTP_ACCOUNT, 'Create SFTP Account'),
                        (REQUEST_TYPE_UPDATE_SFTP_ACCOUNT, 'Update SFTP Account'),
                        )

REQUEST_STATUS_CREATED = 0
REQUEST_STATUS_COMPLETED = 1
REQUEST_STATUS_RETRY = 2
REQUEST_STATUS_FAILED = 3

REQUEST_STATUS_CHOICES = ((REQUEST_STATUS_CREATED,'Created'),
                          (REQUEST_STATUS_COMPLETED,'Completed'),
                          (REQUEST_STATUS_RETRY,'Retry'),
                          (REQUEST_STATUS_FAILED,'Failed'),
                          )

REQUEST_ACTION_CREATE = 0
REQUEST_ACTION_SEND = 1

REQUEST_ACTION_CHOICES = ((REQUEST_STATUS_CREATED,'Created'),
                          (REQUEST_STATUS_RETRY,'Retry'),
                          )