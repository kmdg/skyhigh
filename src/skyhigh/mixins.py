'''
Created on 18 Feb 2013

@author: michael
'''
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.utils.decorators import method_decorator


from unobase.decorators import login_required

class PartnerMixin(object):
    """
    Mixin allows you to require a user with `is_superuser` set to True.
    """
    login_url = settings.LOGIN_URL  # LOGIN_URL from project settings
    raise_exception = False  # Default whether to raise an exception to none
    redirect_field_name = REDIRECT_FIELD_NAME  # Set by django.contrib.auth

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.profile.is_partner:  # If the user doesn't have role,
            if self.raise_exception:  # *and* if an exception was desired
                raise PermissionDenied  # return a forbidden response.
            else:
                return redirect_to_login(request.get_full_path(),
                    self.login_url,
                    self.redirect_field_name)

        return super(PartnerMixin, self).dispatch(request,
            *args, **kwargs)