'''
Created on 15 Jan 2013

@author: euan
'''
from django.conf.urls.defaults import patterns, include, url
from django.views.decorators.csrf import csrf_exempt

from skyhigh.api import mock_handlers
from skyhigh.api import views

urlpatterns = patterns('',

    url(r'^mock/post/success/$', 
        csrf_exempt(mock_handlers.PostSuccessHandler.as_view()),
        name='api_mock_post_success'),

    url(r'^mock/post/failure/$',
        csrf_exempt(mock_handlers.PostFailureHandler.as_view()),
        name='api_mock_post_failure'),


    # API requests
    url(r'^v1/user/exists/$',
        csrf_exempt(views.UserExists.as_view()),
        name='api_user_exists'),
                       
    url(r'^v1/user/action/$',
        csrf_exempt(views.UserAction.as_view()),
        name='api_user_action'),
                       
    url(r'^v1/approve/evaluation/request/$',
        csrf_exempt(views.ApproveEvaluationRequest.as_view()),
        name='api_approve_evaluation_request'),
                       
    url(r'^v1/email/sftp/file/uploaded/$',
        csrf_exempt(views.EmailSFTPFileUploaded.as_view()),
        name='api_email_sftp_file_uploaded'),
                       
    url(r'^v1/email/sftp/account/created/$',
        csrf_exempt(views.EmailSFTPAccountCreated.as_view()),
        name='api_email_sftp_account_created'),

)