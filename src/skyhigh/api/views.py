__author__ = 'michael'

from django.http import HttpResponse
from django.views import generic as generic_views
from django.contrib.auth.models import User

from skyhigh.utils import respond_with_json
from skyhigh import automatic_emails

import json

class APIView(generic_views.View):
    
    def validate_json(self, request):
        try:
            self.json_request = json.loads(request.body)
            return True
        except ValueError:
            return False
        
    def get(self, request, *args, **kwargs):
        if not self.validate_json(request):
            return respond_with_json({'status': 'ERROR',
                                      'message': 'Could not decode JSON object'})
            
    def post(self, request, *args, **kwargs):
        if not self.validate_json(request):
            return respond_with_json({'status': 'ERROR',
                                      'message': 'Could not decode JSON object'})

class UserExists(APIView):

    def get(self, request, *args, **kwargs):
        super(UserExists, self).get(request, *args, **kwargs)

        email = self.json_request.get('email')

        if email is not None:
            try:
                User.objects.get(email=email)
            except User.DoesNotExist:
                return respond_with_json({'status': 'ERROR',
                                          'message': 'User does not exist on our system'})
        else:
            return respond_with_json({'status': 'ERROR',
                                      'message': 'Could not read email address from request'})

        return respond_with_json({'status': 'SUCCESS'})
    
class UserAction(APIView):

    def post(self, request, *args, **kwargs):
        super(UserAction, self).post(request, *args, **kwargs)

        email = self.json_request.get('email')
        action = self.json_request.get('action')
        timestamp = self.json_request.get('timestamp')

        if email is not None:
            try:
                User.objects.get(email=email)
            except User.DoesNotExist:
                return respond_with_json({'status': 'ERROR',
                                          'message': 'User does not exist on our system'})
        else:
            return respond_with_json({'status': 'ERROR',
                                      'message': 'Could not read email address from request'})

        return respond_with_json({'status': 'SUCCESS'})
    
class ApproveEvaluationRequest(APIView):

    def post(self, request, *args, **kwargs):
        super(ApproveEvaluationRequest, self).post(request, *args, **kwargs)

        email = self.json_request.get('email')

        if email is not None:
            try:
                User.objects.get(email=email)
            except User.DoesNotExist:
                return respond_with_json({'status': 'ERROR',
                                          'message': 'User does not exist on our system'})
        else:
            return respond_with_json({'status': 'ERROR',
                                      'message': 'Could not read email address from request'})

        return respond_with_json({'status': 'SUCCESS'})
    
class EmailSFTPAccountCreated(APIView):

    def post(self, request, *args, **kwargs):
        super(EmailSFTPAccountCreated, self).post(request, *args, **kwargs)

        username = self.json_request.get('username')
        password = self.json_request.get('password')

        if username is not None and password is not None:
            automatic_emails.email_sftp_account_created.delay(username, password)
        else:
            return respond_with_json({'status': 'ERROR',
                                      'message': 'Could not read username or password from request'})

        return respond_with_json({'status': 'SUCCESS'})
    
class EmailSFTPFileUploaded(APIView):

    def post(self, request, *args, **kwargs):
        super(EmailSFTPFileUploaded, self).post(request, *args, **kwargs)

        file_path = self.json_request.get('file_path')

        if file_path is not None:
            automatic_emails.email_sftp_file_uploaded.delay(file_path)
        else:
            return respond_with_json({'status': 'ERROR',
                                      'message': 'Could not read file path from request'})

        return respond_with_json({'status': 'SUCCESS'})