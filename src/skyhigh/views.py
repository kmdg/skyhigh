'''
Created on 29 Dec 2012

@author: euan
'''
import urlparse

from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.views import generic as generic_views
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import get_current_site
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.contrib.formtools.wizard.views import NamedUrlSessionWizardView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import base36_to_int

from registration.backends import get_backend

from skyhigh import forms, models, constants, mixins, utils, automatic_emails

from unobase import constants as unobase_constants
from unobase import mixins as unobase_mixins
from unobase import views as unobase_views
from unobase.blog import models as blog_models

import user_actions

def activate(request, backend,
             template_name='registration/activate.html',
             success_url=None, extra_context=None, **kwargs):
    """
    Activate a user's account.

    The actual activation of the account will be delegated to the
    backend specified by the ``backend`` keyword argument (see below);
    the backend's ``activate()`` method will be called, passing any
    keyword arguments captured from the URL, and will be assumed to
    return a ``User`` if activation was successful, or a value which
    evaluates to ``False`` in boolean context if not.

    Upon successful activation, the backend's
    ``post_activation_redirect()`` method will be called, passing the
    ``HttpRequest`` and the activated ``User`` to determine the URL to
    redirect the user to. To override this, pass the argument
    ``success_url`` (see below).

    On unsuccessful activation, will render the template
    ``registration/activate.html`` to display an error message; to
    override thise, pass the argument ``template_name`` (see below).

    **Arguments**

    ``backend``
        The dotted Python import path to the backend class to
        use. Required.

    ``extra_context``
        A dictionary of variables to add to the template context. Any
        callable object in this dictionary will be called to produce
        the end result which appears in the context. Optional.

    ``success_url``
        The name of a URL pattern to redirect to on successful
        acivation. This is optional; if not specified, this will be
        obtained by calling the backend's
        ``post_activation_redirect()`` method.
    
    ``template_name``
        A custom template to use. This is optional; if not specified,
        this will default to ``registration/activate.html``.

    ``\*\*kwargs``
        Any keyword arguments captured from the URL, such as an
        activation key, which will be passed to the backend's
        ``activate()`` method.
    
    **Context:**
    
    The context will be populated from the keyword arguments captured
    in the URL, and any extra variables supplied in the
    ``extra_context`` argument (see above).
    
    **Template:**
    
    registration/activate.html or ``template_name`` keyword argument.
    
    """
    backend = get_backend(backend)
    account = backend.activate(request, **kwargs)

    if account:
        if success_url is None:
            to, args, kwargs = backend.post_activation_redirect(request, account)
            return redirect(to, *args, **kwargs)
        else:
            if account.profile.requested_product_evaluation:
                evaluation_requested = 'evaluator'
            else:
                evaluation_requested = 'user'
                
            return redirect(success_url % {'evaluation_requested': evaluation_requested})

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    return render_to_response(template_name,
                              kwargs,
                              context_instance=context)
    
class PostActivation(generic_views.TemplateView):
    
    def get_context_data(self, **kwargs):
        context = super(PostActivation, self).get_context_data(**kwargs)
        context['evaluation_request'] = self.kwargs['evaluation_requested'] == 'evaluator'
        return context

@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=forms.SkyHighAuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    msg = request.REQUEST.get('msg', '')
    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            netloc = urlparse.urlparse(redirect_to)[1]

            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = settings.LOGIN_REDIRECT_URL
            
            the_user = form.get_user()
            # Okay, security checks complete. Log the user in.
            auth_login(request, the_user)
            user_actions.action_login(the_user)
            
            if the_user.profile.login_count % 5 == 0 and the_user.profile.has_incomplete_fields:
                redirect_to = '/secure/complete_my_profile'

            elif the_user.profile.after_login_url:
                redirect_to = the_user.profile.after_login_url
                the_user.profile.after_login_url = ''
                the_user.profile.save()

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
        print 'Invalid Form: %s' % form.errors
    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'msg': msg,
        'site': current_site,
        'site_name': current_site.name,
    }
    context.update(extra_context or {})
    return render_to_response(template_name, context,
                              context_instance=RequestContext(request, current_app=current_app))
    
def logout(request, next_page=None,
           template_name='registration/logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           current_app=None, extra_context=None):
    """
    Logs out the user and displays 'You are logged out' message.
    """
    the_user = request.user
    auth_logout(request)
    user_actions.action_logout(the_user)
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if redirect_to:
        netloc = urlparse.urlparse(redirect_to)[1]
        # Security check -- don't allow redirection to a different host.
        if not (netloc and netloc != request.get_host()):
            return HttpResponseRedirect(redirect_to)

    if next_page is None:
        current_site = get_current_site(request)
        context = {
            'site': current_site,
            'site_name': current_site.name,
            'title': 'Logged out'
        }
        if extra_context is not None:
            context.update(extra_context)
        return TemplateResponse(request, template_name, context,
                                current_app=current_app)
    else:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page or request.path)
    
# Doesn't need csrf_protect since no-one can guess the URL
@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb36=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    assert uidb36 is not None and token is not None # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('django.contrib.auth.views.password_reset_complete')
    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(id=uid_int)
    except (ValueError, User.DoesNotExist):
        user = None
        
    print token_generator.check_token(user, token)

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(None)
    else:
        validlink = False
        form = None
    context = {
        'form': form,
        'validlink': validlink,
        'user_id': uid_int
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)
    
class PasswordResetNewToken(generic_views.TemplateView):
    
    def get(self, request, *args, **kwargs):
        automatic_emails.email_password_reset_new_token.delay(self.kwargs['user_id'])
        
        return super(PasswordResetNewToken, self).get(request, *args, **kwargs)
    
class RequestEvaluation(generic_views.FormView):
    
    def get_initial(self):
        if self.request.user.is_authenticated:
            return {'user' : self.request.user,
                    'request': self.request}
        return {'request': self.request}

    def get_success_url(self):
#        if self.request.user.is_authenticated():
#            return reverse('product_evaluation_thanks')
#
#        return reverse('complete_evaluation_signup')

        return reverse('product_evaluation_thanks')
    
    def form_valid(self, form):
        evaluation_request = form.save()

        #if form.cleaned_data['email']:
        #    self.request.session['email'] = form.cleaned_data['email']

        return super(RequestEvaluation, self).form_valid(form)
    
    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_authenticated() and request.user.evaluation_request:
                return HttpResponseRedirect(reverse('product_evaluation_already_submitted'))
        except models.ProductEvaluation.DoesNotExist:
            pass
        return super(RequestEvaluation, self).get(request, *args, **kwargs)
    
class Partner(generic_views.FormView):
    def get_initial(self):
        if self.request.user.is_authenticated:
            return {'user' : self.request.user,
                    'request': self.request}
        return {'request': self.request}

    def get_success_url(self):
        if self.request.user.is_authenticated():
            return reverse('partners_overview')

        return reverse('complete_partner_signup')

    def form_valid(self, form):
        partnership = form.save()

        if form.cleaned_data['email']:
            self.request.session['email'] = form.cleaned_data['email']

        return super(Partner, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_authenticated() and request.user.partnership:
                return HttpResponseRedirect(reverse('partnership_application_already_submitted'))
        except models.Partnership.DoesNotExist:
            pass

        return super(Partner, self).get(request, *args, **kwargs)
    

class TechnologyPartner(Partner):
    pass
    
class CloudServiceProviderPartner(Partner):
    pass

class ChannelPartner(Partner):
    pass
    
class DealOverview(mixins.PartnerMixin, generic_views.TemplateView):
    raise_exception = True
    
class DealRequest(mixins.PartnerMixin, generic_views.FormView):
    
    raise_exception = True

    def get_initial(self):
        if self.request.user.is_authenticated:
            return {'user' : self.request.user,
                    'request': self.request}
        return {'request': self.request}

    def get_success_url(self):
        return reverse('partners_resources')

    def form_valid(self, form):
        partnership = form.save()
            
        messages.success(self.request, 'Deal has been submitted.')

        return super(DealRequest, self).form_valid(form)
    
    def form_invalid(self, form):
        print form.errors
    
class ContactInfoRequest(generic_views.FormView):
    
    def get_initial(self):
        if self.request.user.is_authenticated:
            return {'user' : self.request.user,
                    'request': self.request}
        return {'request': self.request}

    def get_success_url(self):
        if self.request.user.is_authenticated():
            return reverse('company_contact_info_request_thanks')

        return reverse('complete_contact_info_signup')
    
    def form_valid(self, form):
        contact_message = form.save()

        if form.cleaned_data['email']:
            self.request.session['email'] = form.cleaned_data['email']

        return super(ContactInfoRequest, self).form_valid(form)

class CareerApplication(generic_views.FormView):

    def get_initial(self):
        if self.request.user.is_authenticated:
            return {'user' : self.request.user,
                    'request': self.request,
                    'position': models.Career.objects.get(pk=self.kwargs['pk'])}

        return {'request': self.request,
                'position': models.Career.objects.get(pk=self.kwargs['pk'])}

    def get_success_url(self):
        if self.request.user.is_authenticated():
            return reverse('partners_overview')

        return reverse('company_careers_complete_signup')

    def form_valid(self, form):
        career_position = form.save()

        if form.cleaned_data['email']:
            self.request.session['email'] = form.cleaned_data['email']

        return super(CareerApplication, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        try:
            if request.user.is_authenticated() and request.user.career_application:
                return HttpResponseRedirect(reverse('company_careers_application_already_submitted'))
        except models.CareerApplication.DoesNotExist:
            pass

        return super(CareerApplication, self).get(request, *args, **kwargs)

class NewsOverview(generic_views.TemplateView):

    def get_context_data(self, **kwargs):
        context = {'event_list': models.Event.objects.filter(state=unobase_constants.STATE_PUBLISHED).order_by('start_date')[:3],
                   'media_coverage_list': models.MediaCoverage.objects.filter(state=unobase_constants.STATE_PUBLISHED)[:3],
                   'press_release_list': models.PressRelease.objects.filter(state=unobase_constants.STATE_PUBLISHED)[:3]
        }

        context.update(kwargs)

        return super(NewsOverview, self).get_context_data(**context)
    
class EventList(generic_views.ListView):
    
    def get_queryset(self):
        return models.Event.permitted.all().order_by('start_date')

class CareerList(generic_views.ListView):

    def get_queryset(self):
        return models.Career.permitted.all()

class MediaCoverageList(generic_views.ListView):
    
    def get_queryset(self):
        return models.MediaCoverage.permitted.all()

class PressReleaseList(generic_views.ListView):
    
    def get_queryset(self):
        return models.PressRelease.permitted.all()

class PressReleaseDetail(generic_views.DetailView):

    def get_object(self):
        return get_object_or_404(models.PressRelease,
            pk=self.kwargs['pk'])
        
class LeadershipList(generic_views.ListView):
    
    def get_queryset(self):
        return models.Leader.permitted.all()

class LeadershipDetail(generic_views.DetailView):

    def get_object(self):
        return get_object_or_404(models.Leader,
            pk=self.kwargs['pk'])
        
class InvestorList(generic_views.ListView):
    
    def get_queryset(self):
        return models.Investor.permitted.all()

class InvestorDetail(generic_views.DetailView):

    def get_object(self):
        return get_object_or_404(models.Investor,
            pk=self.kwargs['pk'])
        
class CaseStudyList(generic_views.ListView):
    
    def get_queryset(self):
        return models.CaseStudy.permitted.all()

class CaseStudyDetail(generic_views.DetailView):

    def get_object(self):
        return get_object_or_404(models.CaseStudy,
            pk=self.kwargs['pk'])
    
class MyProfile(unobase_mixins.LoginRequiredMixin, generic_views.UpdateView):
    
    def get_object(self):
        return self.request.user.profile
    
    def get_initial(self):
        return {'instance' : self.request.user.profile}
    
    def form_valid(self, form):
        self.object = form.save()

        user_actions.action_profile_update(self.object.user)
        
        messages.success(self.request, 'Profile details updated.')
        
        if form.old_email != form.cleaned_data['email']:
            self.object.revalidate_email(form.old_email)
            messages.success(self.request, 'You will need to re-authenticate your account before you may login again.')
            return HttpResponseRedirect(reverse('logout'))

        return self.render_to_response(self.get_context_data(form=form))
    
class LogFileSampleUpload(unobase_mixins.LoginRequiredMixin, generic_views.FormView):
    
    def get_initial(self):
        return {'user' : self.request.user}
    
    def form_valid(self, form):
        self.object = form.save()
        
        messages.success(self.request, 'Log file sample uploaded.')

        return self.render_to_response(self.get_context_data(form=form))
    
class SFTPAccountList(unobase_mixins.LoginRequiredMixin, generic_views.ListView):

    def get_queryset(self):
        return models.SFTPUser.objects.filter(user=self.request.user)
    
class SFTPAccountUpdate(unobase_mixins.LoginRequiredMixin, generic_views.UpdateView):

    def get_queryset(self):
        return models.SFTPUser.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        self.object = form.save()
        
        messages.success(self.request, 'SFTP account details updated.')
        
        return self.render_to_response(self.get_context_data(form=form))

class MyProfileCSPAttributesUpdate(unobase_mixins.RoleCheckMixin, NamedUrlSessionWizardView):

    role_required = constants.ROLE_CHOICE_CLOUD_SERVICE_PROVIDER
    raise_exception = True
    role_only = True

    def get_template_names(self):
        """
        Return the directory and describe naming convention of
        workshop wizard forms.
        """
        step = self.steps.step1
        return 'skyhigh/my_profile_csp_attributes_update_%s.html' % step

    def get_form_initial(self, step):
        if self.request.user.is_authenticated:
            return self.initial_dict.get(step, {'user' : self.request.user})
        return self.initial_dict.get(step, {})

    def process_step(self, form):
        form.save()

        return self.get_form_step_data(form)

    def done(self, form_list, **kwargs):
        messages.success(self.request, 'CSP Attributes updated.')
        
        return HttpResponseRedirect('/secure/my_profile/')

class NewsletterSignup(generic_views.FormView):

    def get_initial(self):
        if self.request.user.is_authenticated:
            return {'user' : self.request.user,
                    'request': self.request}
        return {'request': self.request}

    def get_success_url(self):
        if self.request.user.is_authenticated():
            return reverse('newsletter_signup_thankyou')

        return reverse('secure_complete_newsletter_signup')

    def form_valid(self, form):
        form.save()

        if form.cleaned_data['newsletter_email']:
            self.request.session['email'] = form.cleaned_data['newsletter_email']

        return super(NewsletterSignup, self).form_valid(form)

    def form_invalid(self, form):
        return HttpResponseRedirect(self.request.META['HTTP_REFERER'])

class CompleteSignup(generic_views.FormView):

    def get_initial(self):
        email = self.request.session.get('email', None)

        if email:
            return {'email' : email}
        return {}

    def form_valid(self, form):
        form.save()

        return super(CompleteSignup, self).form_valid(form)

class CompleteNewsletterSignup(CompleteSignup):
    pass

class CompleteContactInfoSignup(CompleteSignup):
    pass

class CompleteEvaluationSignup(CompleteSignup):
    pass

class CompletePartnerSignup(CompleteSignup):
    pass

class CompleteCareerSignup(CompleteSignup):
    pass

class MarketingEmailsUnsubscribeExternal(unobase_mixins.LoginRequiredMixin, generic_views.TemplateView):
    
    def get(self, request, *args, **kwargs):
        request.user.profile.newsletter_recipient = False
        request.user.profile.receive_marketing_emails = False
        request.user.profile.save()
        
        return super(MarketingEmailsUnsubscribeExternal, self).get(request, *args, **kwargs)

class MarketingEmailsUnsubscribe(generic_views.TemplateView):
    
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs['user_id'])
        
        if not self.kwargs['token'] == utils.get_token_for_user(user):
            raise Http404, "Token did not match"
        
        user.profile.newsletter_recipient = False
        user.profile.receive_marketing_emails = False
        user.profile.save()
        
        return super(MarketingEmailsUnsubscribe, self).get(request, *args, **kwargs)
    
class Resources(generic_views.TemplateView):
    
    def get_context_data(self, **kwargs):
        context = super(Resources, self).get_context_data(**kwargs)
        
        resources = models.Resource.objects.all()
        
        try:
            featured_resource = resources.filter(featured=True)[0]
        except IndexError:
            featured_resource = None
        
        context.update({
            'featured_resource': featured_resource,
            'whitepapers': resources.filter(type='whitepapers'),
            'datasheets': resources.filter(type='datasheets'),
            'videos': resources.filter(type='videos'),
            'on_demand_webinars': resources.filter(type='ondemandwebinars')
        })
        
        return context
    
class Whitepapers(generic_views.ListView):
    
    def get_queryset(self):
        return models.Resource.objects.filter(type='whitepapers')
    
class Datasheets(generic_views.ListView):
    
    def get_queryset(self):
        return models.Resource.objects.filter(type='datasheets')

class Videos(generic_views.ListView):
    
    def get_queryset(self):
        return models.Resource.objects.filter(type='videos')
    
class Webinars(generic_views.ListView):
    
    def get_queryset(self):
        return models.Resource.objects.filter(type='ondemandwebinars')
    
class BlogDetail(unobase_views.ListWithDetailView):

    def get_object(self):
        return get_object_or_404(blog_models.Blog,
            state=unobase_constants.STATE_PUBLISHED, slug=self.kwargs['slug'])

    def get_queryset(self):
        if self.request.GET.has_key('filter_by_tag') and self.request.GET['filter_by_tag'].strip():
            return blog_models.BlogEntry.objects.filter(tags__title__iexact=self.request.GET['filter_by_tag'].strip()).order_by('-publish_date_time')

        return blog_models.BlogEntry.objects.filter(blog=self.object).order_by('-publish_date_time')
    