from django.conf import settings

def project_settings(request):
    return {'DEBUG' : settings.DEBUG}