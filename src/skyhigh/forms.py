'''
Created on 29 Dec 2012

@author: euan
'''
from django import forms
from django.db.models import Q
from django.conf import settings
from django.template import loader
from django.forms.util import ErrorList
from django.utils.http import int_to_base36
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.sites.models import Site, get_current_site
from django.forms.formsets import formset_factory

from skyhigh import models, utils, user_actions, constants, automatic_emails
import re

class CleanEmailRegistrationMixin(object):
    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError('This email address is already in use. Please supply a different email address.')
        return self.cleaned_data['email']

class CleanEmailExistingMixin(object):
    def clean_email(self):
        if self.user is not None:
            if not self.user.email == self.cleaned_data['email']:
                raise forms.ValidationError('You cannot change your email address half-way though.')
        else:
            if User.objects.filter(email__iexact=self.cleaned_data['email']):
                raise forms.ValidationError('This email address already has an account with us. Please log in to complete this request.')
        return self.cleaned_data['email']

class CleanPasswordMixin(object):

    def clean_password1(self):
        """
        Verify password is strong and matches criteria

        """
        if 'password1' in self.cleaned_data and self.cleaned_data['password1']:
            PWD_MIN_CHAR = 8
            PWD_MAX_CHAR = 45

            pattern = "(?=^.{%i,%i}$)((?=.*\\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^A-Za-z0-9]))^.*" % (PWD_MIN_CHAR, PWD_MAX_CHAR)

            if re.match(pattern, self.cleaned_data['password1']) is None:
                raise forms.ValidationError('Valid password should contain at least %i alphanumeric characters. Contain both upper and lower case letters. Contain at least one number (for example, 0-9). Contain at least one special character (for example,!@#$%%^&*()+=-[]\\\';,./{}|\":?~_<>)' % PWD_MIN_CHAR)

        return self.cleaned_data['password1']

    def clean_password2(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] and self.cleaned_data['password2']:
                if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                    raise forms.ValidationError('The password fields didn\'t match: Password confirmation failed.')
            return self.cleaned_data['password2']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] and self.cleaned_data['password2']:
                if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                    raise forms.ValidationError('The two password fields didn\'t match.')
        return self.cleaned_data
    
class SearchEnginePPCInfoMixin(forms.Form):
    search_string = forms.CharField(max_length=255, widget=forms.HiddenInput, required=False)
    search_engine = forms.CharField(max_length=255, widget=forms.HiddenInput, required=False)
    pay_per_click_keyword = forms.CharField(max_length=255, widget=forms.HiddenInput, required=False)

class SkyHighRegistrationForm(SearchEnginePPCInfoMixin, CleanPasswordMixin, CleanEmailRegistrationMixin):
    """
    Form for registering a new user account.
    
    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.
    
    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.
    
    """
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=75)
    company = forms.CharField(max_length=128)
    job_title = forms.CharField(max_length=32, required=False)
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    request_evaluation = forms.BooleanField(required=False)
    request_partnership = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(SkyHighRegistrationForm, self).__init__(*args, **kwargs)

        self.user = None

        self.fields['first_name'].widget.attrs.update({'class':'required'})
        self.fields['last_name'].widget.attrs.update({'class':'required'})
        self.fields['email'].widget.attrs.update({'class':'required'})
        self.fields['company'].widget.attrs.update({'class':'required'})
        self.fields['password1'].widget.attrs.update({'class':'required'})
        self.fields['password2'].widget.attrs.update({'class':'required'})
    
class SkyHighAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Email address', max_length=75)
    
class SkyHighPasswordResetForm(PasswordResetForm):
    
    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             txt_email_template_name='registration/password_reset_email.txt',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            
            text_content = render_to_string('registration/activation_email.txt', c)
            
            utils.send_mail(email_template_name, c, subject, text_content, 
                            settings.DEFAULT_FROM_EMAIL, [user.email,], None)

class ReadOnlyProfileAttributesForm(SearchEnginePPCInfoMixin, CleanEmailExistingMixin):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=75)
    company = forms.CharField(max_length=128)
    job_title = forms.CharField(max_length=32)
    phone_number = forms.CharField(max_length=16, required=False)
    zip_postal_code = forms.CharField(max_length=8, required=False)
    requests_or_comments = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(ReadOnlyProfileAttributesForm, self).__init__(*args, **kwargs)

        self.user = None
        self.request = kwargs['initial'].get('request')

        if kwargs['initial'].has_key('user') and kwargs['initial']['user'].is_authenticated():
            self.user = kwargs['initial']['user']
            self.fields['first_name'].initial = self.user.profile.first_name
            self.fields['first_name'].widget.attrs.update({'readonly':'readonly'})
            self.fields['last_name'].initial = self.user.profile.last_name
            self.fields['last_name'].widget.attrs.update({'readonly':'readonly'})
            self.fields['email'].initial = self.user.profile.email
            self.fields['email'].widget.attrs.update({'readonly':'readonly'})
            
            if self.user.profile.phone_number:
                self.fields['phone_number'].initial = self.user.profile.phone_number
                self.fields['phone_number'].widget.attrs.update({'readonly':'readonly'})
                
            if self.user.profile.zip_postal_code:
                self.fields['zip_postal_code'].initial = self.user.profile.zip_postal_code
                self.fields['zip_postal_code'].widget.attrs.update({'readonly':'readonly'})

            if self.user.profile.company:
                self.fields['company'].initial = self.user.profile.company
                self.fields['company'].widget.attrs.update({'readonly':'readonly'})

            if self.user.profile.job_title:
                self.fields['job_title'].initial = self.user.profile.job_title
                self.fields['job_title'].widget.attrs.update({'readonly':'readonly'})
                
        self.fields['first_name'].widget.attrs.update({'class':'required'})
        self.fields['last_name'].widget.attrs.update({'class':'required'})
        self.fields['email'].widget.attrs.update({'class':'required'})
        self.fields['company'].widget.attrs.update({'class':'required'})
    
    def clean_zip_postal_code(self):
        if self.cleaned_data['zip_postal_code'] and not self.cleaned_data['zip_postal_code'].isdigit():
            raise forms.ValidationError(
                "Please provide a valid number."
            )
        return self.cleaned_data['zip_postal_code']

    def save(self):
        try:
            self.profile = models.Profile.objects.get(email=self.cleaned_data['email'])

            company = self.cleaned_data['company']
            job_title = self.cleaned_data['job_title']

            if company != self.profile.company or \
               job_title != self.profile.job_title:
                self.profile.company = company
                self.profile.job_title = job_title
                self.profile.save()
        except models.Profile.DoesNotExist:
            self.profile = models.SkyHighRegistrationProfile.objects.create_inactive_profile(site=Site.objects.get_current(),
                request=self.request,
                send_email=False,
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                company=self.cleaned_data['company'],
                job_title=self.cleaned_data['job_title'],
                phone_number=self.cleaned_data['phone_number'],
                zip_postal_code=self.cleaned_data['zip_postal_code'],
                requests_or_comments=self.cleaned_data['requests_or_comments'],
                search_string=self.cleaned_data['search_string'],
                search_engine=self.cleaned_data['search_engine'],
                pay_per_click_keyword=self.cleaned_data['pay_per_click_keyword']
            )
            
class LogFileSampleForm(forms.Form):
    log_file_sample = forms.CharField(widget=forms.Textarea)
    
    def __init__(self, *args, **kwargs):
        super(LogFileSampleForm, self).__init__(*args, **kwargs)
        self.user = self.initial.get('user')
        product_evaluation = models.ProductEvaluation.objects.get(user=self.user)
        self.fields['log_file_sample'].initial = product_evaluation.log_file_sample
    
    def save(self):
        product_evaluation = models.ProductEvaluation.objects.get(user=self.user)
        product_evaluation.log_file_sample = self.cleaned_data['log_file_sample']
        product_evaluation.save()
        
        return product_evaluation

class RequestEvaluationForm(ReadOnlyProfileAttributesForm, CleanPasswordMixin):
    upload_log_file_sample = forms.BooleanField(required=False)
    log_file_sample = forms.CharField(widget=forms.Textarea, required=False)
    password1 = forms.CharField(widget=forms.PasswordInput(), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(), required=False)
    
    def __init__(self, *args, **kwargs):
        super(RequestEvaluationForm, self).__init__(*args, **kwargs)
        
        if self.user is None:
            self.fields['password1'].required = True
            self.fields['password1'].widget.attrs.update({'class': 'required'})
            self.fields['password2'].required = True
            self.fields['password2'].widget.attrs.update({'class': 'required'})
        
        self.fields['job_title'].required = False
        self.fields['phone_number'].required = False
        self.fields['zip_postal_code'].required = False
    
    def save(self):
        super(RequestEvaluationForm, self).save()
        
        if self.user is None:
            self.profile.set_password(self.cleaned_data['password1'])
    
            self.profile.save()
    
            registration_profile = models.SkyHighRegistrationProfile.objects.get(user=self.profile.user)
            automatic_emails.email_account_activation.delay(registration_profile.id, Site.objects.get_current().id)

        user_actions.action_product_evaluation_request(self.profile.user)

        return models.ProductEvaluation.objects.create(user=self.profile.user, 
                                                       log_file_sample=self.cleaned_data['log_file_sample'])

class ContactInfoRequestForm(ReadOnlyProfileAttributesForm):
    message = forms.CharField(widget=forms.Textarea)
    
    def __init__(self, *args, **kwargs):
        super(ContactInfoRequestForm, self).__init__(*args, **kwargs)

        self.fields['message'].widget.attrs.update({'rows':'10', 'cols':'68'})
    
    def save(self):
        super(ContactInfoRequestForm, self).save()

        user_actions.action_contact_message_sent(self.profile.user)

        return models.ContactMessage.objects.create(user=self.profile.user, message=self.cleaned_data['message'])
    
class PartnerFormMixin(forms.Form):
    num_branches = forms.IntegerField(required=False)
    branch_offices = forms.CharField(max_length=255, required=False)
    countries_requesting_to_sell_in = forms.CharField(max_length=255, required=False)
    us_states_requesting_to_sell_in = forms.CharField(max_length=255, required=False)
    annual_revenue = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    years_in_business = forms.IntegerField(required=False)
    num_sales_reps = forms.IntegerField(required=False)
    num_systems_engineers = forms.IntegerField(required=False)
    num_technical_support_staff = forms.IntegerField(required=False)
    business_type = forms.ChoiceField(choices=constants.BUSINESS_TYPE_CHOICES, required=False)
    preferred_distributor = forms.CharField(max_length=255, required=False)
    target_vertical_focus = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                                           queryset=models.TargetVerticalFocus.objects.all(), required=False)
    resell_to_usa_federal_sectors = forms.ChoiceField(choices=constants.RESELL_TO_USA_FEDERAL_SECTOR_CHOICES, required=False)
    offer_own_support = forms.ChoiceField(choices=constants.OFFER_OWN_SUPPORT_CHOICES, required=False)
    manufacturers_selling = forms.CharField(max_length=255, required=False)
    leading_competitors = forms.CharField(max_length=255, required=False)
    additional_comments = forms.CharField(widget=forms.Textarea, required=False)
    representitive = forms.CharField(max_length=255, required=False)
    vat_number = forms.CharField(max_length=255, required=False)
    gst_number = forms.CharField(max_length=255, required=False)
    tax_id_number = forms.CharField(max_length=255, required=False)
    d_and_b_number = forms.CharField(max_length=255, required=False)
    type_of_technology_selling = forms.CharField(max_length=255, required=False)
    
    def save_partnership_fields(self):
        if self.cleaned_data['num_branches']:
            self.partnership.num_branches = self.cleaned_data['num_branches']
            
        if self.cleaned_data['branch_offices']:
            self.partnership.branch_offices = self.cleaned_data['branch_offices']
            
        if self.cleaned_data['countries_requesting_to_sell_in']:
            self.partnership.countries_requesting_to_sell_in = self.cleaned_data['countries_requesting_to_sell_in']
            
        if self.cleaned_data['us_states_requesting_to_sell_in']:
            self.partnership.us_states_requesting_to_sell_in = self.cleaned_data['us_states_requesting_to_sell_in']
            
        if self.cleaned_data['annual_revenue']:
            self.partnership.annual_revenue = self.cleaned_data['annual_revenue']
            
        if self.cleaned_data['years_in_business']:
            self.partnership.years_in_business = self.cleaned_data['years_in_business']
            
        if self.cleaned_data['num_sales_reps']:
            self.partnership.num_sales_reps = self.cleaned_data['num_sales_reps']
            
        if self.cleaned_data['num_systems_engineers']:
            self.partnership.num_systems_engineers = self.cleaned_data['num_systems_engineers']
            
        if self.cleaned_data['num_technical_support_staff']:
            self.partnership.num_technical_support_staff = self.cleaned_data['num_technical_support_staff']
            
        if self.cleaned_data['business_type']:
            self.partnership.business_type = self.cleaned_data['business_type']
            
        if self.cleaned_data['preferred_distributor']:
            self.partnership.preferred_distributor = self.cleaned_data['preferred_distributor']
            
        if self.cleaned_data['target_vertical_focus']:
            self.partnership.target_vertical_focus = self.cleaned_data['target_vertical_focus']
            
        if self.cleaned_data['resell_to_usa_federal_sectors']:
            self.partnership.resell_to_usa_federal_sectors = self.cleaned_data['resell_to_usa_federal_sectors']
            
        if self.cleaned_data['offer_own_support']:
            self.partnership.offer_own_support = self.cleaned_data['offer_own_support']
            
        if self.cleaned_data['manufacturers_selling']:
            self.partnership.manufacturers_selling = self.cleaned_data['manufacturers_selling']
            
        if self.cleaned_data['leading_competitors']:
            self.partnership.leading_competitors = self.cleaned_data['leading_competitors']
            
        if self.cleaned_data['additional_comments']:
            self.partnership.additional_comments = self.cleaned_data['additional_comments']
            
        if self.cleaned_data['representitive']:
            self.partnership.representitive = self.cleaned_data['representitive']
            
        if self.cleaned_data['vat_number']:
            self.partnership.vat_number = self.cleaned_data['vat_number']
            
        if self.cleaned_data['gst_number']:
            self.partnership.gst_number = self.cleaned_data['gst_number']
            
        if self.cleaned_data['tax_id_number']:
            self.partnership.tax_id_number = self.cleaned_data['tax_id_number']
            
        if self.cleaned_data['d_and_b_number']:
            self.partnership.d_and_b_number = self.cleaned_data['d_and_b_number']
            
        if self.cleaned_data['type_of_technology_selling']:
            self.partnership.type_of_technology_selling = self.cleaned_data['type_of_technology_selling']
        
        self.partnership.save()
        
class DealForm(ReadOnlyProfileAttributesForm, PartnerFormMixin):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)
    
    def __init__(self, *args, **kwargs):
        super(DealForm, self).__init__(*args, **kwargs)
        
        if self.user.profile.is_partner:
            self.fields['num_branches'].initial = self.user.profile.partnership.num_branches
            self.fields['branch_offices'].initial = self.user.profile.partnership.branch_offices
            self.fields['countries_requesting_to_sell_in'].initial = self.user.profile.partnership.countries_requesting_to_sell_in
            self.fields['us_states_requesting_to_sell_in'].initial = self.user.profile.partnership.us_states_requesting_to_sell_in
            self.fields['annual_revenue'].initial = self.user.profile.partnership.annual_revenue
            self.fields['years_in_business'].initial = self.user.profile.partnership.years_in_business
            self.fields['num_sales_reps'].initial = self.user.profile.partnership.num_sales_reps
            self.fields['num_systems_engineers'].initial = self.user.profile.partnership.num_systems_engineers
            self.fields['num_technical_support_staff'].initial = self.user.profile.partnership.num_technical_support_staff
            self.fields['business_type'].initial = self.user.profile.partnership.business_type
            self.fields['preferred_distributor'].initial = self.user.profile.partnership.preferred_distributor
            self.fields['target_vertical_focus'].initial = self.user.profile.partnership.target_vertical_focus.all()
            self.fields['resell_to_usa_federal_sectors'].initial = self.user.profile.partnership.resell_to_usa_federal_sectors
            self.fields['offer_own_support'].initial = self.user.profile.partnership.offer_own_support
            self.fields['manufacturers_selling'].initial = self.user.profile.partnership.manufacturers_selling
            self.fields['leading_competitors'].initial = self.user.profile.partnership.leading_competitors
            self.fields['additional_comments'].initial = self.user.profile.partnership.additional_comments
            self.fields['representitive'].initial = self.user.profile.partnership.representitive
            self.fields['vat_number'].initial = self.user.profile.partnership.vat_number
            self.fields['gst_number'].initial = self.user.profile.partnership.gst_number
            self.fields['tax_id_number'].initial = self.user.profile.partnership.tax_id_number
            self.fields['d_and_b_number'].initial = self.user.profile.partnership.d_and_b_number
    
    def save(self):
        super(DealForm, self).save()
        
        if self.user.profile.is_partner:
            self.partnership = self.profile.partnership
            
            deal = models.Deal.objects.create(partner=self.partnership,
                                   title=self.cleaned_data['title'], 
                                   content=self.cleaned_data['content'])
            
            self.save_partnership_fields()
            
            user_actions.action_deal_request_submitted(self.profile.user)

            return deal
        
        return None

class TechnologyPartnerForm(ReadOnlyProfileAttributesForm, PartnerFormMixin):
    url = forms.URLField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(TechnologyPartnerForm, self).__init__(*args, **kwargs)
        
        self.fields['business_type'].choices = constants.TECHNOLOGY_BUSINESS_TYPE_CHOICES

    def save(self):
        super(TechnologyPartnerForm, self).save()
        
        if self.cleaned_data['url']:
            self.profile.website = self.cleaned_data['url']
            self.profile.save()

        self.partnership = models.Partnership.objects.create(user=self.profile.user, type=constants.PARTNER_TYPE_TECHNOLOGY)
            
        self.save_partnership_fields()

        user_actions.action_partnership_request(self.profile.user)
        automatic_emails.email_technical_partner_request.delay(self.profile.user.id)

        return self.partnership
    
class CloudServiceProviderForm(ReadOnlyProfileAttributesForm, PartnerFormMixin):
    url = forms.URLField(required=False)
    category = forms.ChoiceField(required=False, choices=constants.CSP_CATEGORY_CHOICES)

    def save(self):
        super(CloudServiceProviderForm, self).save()

        self.partnership = models.Partnership.objects.create(user=self.profile.user, type=constants.PARTNER_TYPE_TECHNOLOGY)

        models.CloudServiceProvider.objects.create(partnership=self.partnership,
            url=self.cleaned_data['url'],
            category=int(self.cleaned_data['category']) if self.cleaned_data['category'] else 0)
            
        self.save_partnership_fields()

        user_actions.action_partnership_request(self.profile.user)
        automatic_emails.email_technical_partner_request.delay(self.profile.user.id)

        return self.partnership

class ChannelPartnerForm(ReadOnlyProfileAttributesForm, PartnerFormMixin):
    type = forms.ChoiceField(choices=constants.CHANNEL_PARTNER_TYPE_CHOICES,
        initial=constants.CHANNEL_PARTNER_TYPE_RESELLER, widget=forms.RadioSelect())

    def save(self):
        super(ChannelPartnerForm, self).save()

        self.partnership = models.Partnership.objects.create(user=self.profile.user, type=constants.PARTNER_TYPE_CHANNEL)

        partnership_type = int(self.cleaned_data['type'])

        if partnership_type == constants.CHANNEL_PARTNER_TYPE_RESELLER:
            models.Reseller.objects.create(partnership=self.partnership)
        elif partnership_type == constants.CHANNEL_PARTNER_TYPE_DISTRIBUTOR:
            models.Distributor.objects.create(partnership=self.partnership)
            
        self.save_partnership_fields()

        user_actions.action_partnership_request(self.profile.user)
        automatic_emails.email_channel_partner_request.delay(self.profile.user.id)

        return self.partnership

class CareerApplicationForm(ReadOnlyProfileAttributesForm):
    position = forms.ModelChoiceField(queryset=models.Career.objects.all().only('position'))
    cv_file = forms.FileField(required=False)
    message = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(CareerApplicationForm, self).__init__(*args, **kwargs)

        self.fields['position'].initial = kwargs['initial'].get('position')

    def save(self):
        super(CareerApplicationForm, self).save()

        career_application = models.CareerApplication.objects.create(user=self.profile.user,
            career=self.cleaned_data['position'],
            cv_file=self.cleaned_data['cv_file'],
            message=self.cleaned_data['message']
        )

        return career_application

class MyProfileForm(forms.ModelForm):
    num_branches = forms.IntegerField(required=False)
    branch_offices = forms.CharField(max_length=255, required=False)
    countries_requesting_to_sell_in = forms.CharField(max_length=255, required=False)
    us_states_requesting_to_sell_in = forms.CharField(max_length=255, required=False)
    annual_revenue = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    years_in_business = forms.IntegerField(required=False)
    num_sales_reps = forms.IntegerField(required=False)
    num_systems_engineers = forms.IntegerField(required=False)
    num_technical_support_staff = forms.IntegerField(required=False)
    business_type = forms.ChoiceField(choices=constants.BUSINESS_TYPE_CHOICES, required=False)
    preferred_distributor = forms.CharField(max_length=255, required=False)
    target_vertical_focus = forms.ModelMultipleChoiceField(queryset=models.TargetVerticalFocus.objects.all(), required=False)
    resell_to_usa_federal_sectors = forms.ChoiceField(choices=constants.RESELL_TO_USA_FEDERAL_SECTOR_CHOICES, required=False)
    offer_own_support = forms.ChoiceField(choices=constants.OFFER_OWN_SUPPORT_CHOICES, required=False)
    manufacturers_selling = forms.CharField(max_length=255, required=False)
    leading_competitors = forms.CharField(max_length=255, required=False)
    additional_comments = forms.CharField(widget=forms.Textarea, required=False)
    representitive = forms.CharField(max_length=255, required=False)
    vat_number = forms.CharField(max_length=255, required=False)
    gst_number = forms.CharField(max_length=255, required=False)
    tax_id_number = forms.CharField(max_length=255, required=False)
    d_and_b_number = forms.CharField(max_length=255, required=False)
    
    class Meta:
        model = models.Profile
        fields = ('title', 'first_name', 'last_name', 'email', 'phone_number',
                  'mobile_number', 'address', 'city', 'state_province', 'country',
                  'company', 'job_title', 'industry', 'num_employees', 'requests_or_comments',
                  'heard_about_from', 'website', 'zip_postal_code')
        
    def __init__(self, *args, **kwargs):
        super(MyProfileForm, self).__init__(*args, **kwargs)
        
        self.fields['first_name'].required = True
        self.fields['first_name'].widget.attrs.update({'class':'required'})
        self.fields['last_name'].required = True
        self.fields['last_name'].widget.attrs.update({'class':'required'})
        self.fields['email'].required = True
        self.fields['email'].widget.attrs.update({'class':'required email'})
        
        self.old_email = self.instance.email
        
        if self.instance.is_partner:
            self.fields['num_branches'].initial = self.instance.partnership.num_branches
            self.fields['branch_offices'].initial = self.instance.partnership.branch_offices
            self.fields['countries_requesting_to_sell_in'].initial = self.instance.partnership.countries_requesting_to_sell_in
            self.fields['us_states_requesting_to_sell_in'].initial = self.instance.partnership.us_states_requesting_to_sell_in
            self.fields['annual_revenue'].initial = self.instance.partnership.annual_revenue
            self.fields['years_in_business'].initial = self.instance.partnership.years_in_business
            self.fields['num_sales_reps'].initial = self.instance.partnership.num_sales_reps
            self.fields['num_systems_engineers'].initial = self.instance.partnership.num_systems_engineers
            self.fields['num_technical_support_staff'].initial = self.instance.partnership.num_technical_support_staff
            self.fields['business_type'].initial = self.instance.partnership.business_type
            self.fields['preferred_distributor'].initial = self.instance.partnership.preferred_distributor
            self.fields['target_vertical_focus'].initial = self.instance.partnership.target_vertical_focus.all()
            self.fields['resell_to_usa_federal_sectors'].initial = self.instance.partnership.resell_to_usa_federal_sectors
            self.fields['offer_own_support'].initial = self.instance.partnership.offer_own_support
            self.fields['manufacturers_selling'].initial = self.instance.partnership.manufacturers_selling
            self.fields['leading_competitors'].initial = self.instance.partnership.leading_competitors
            self.fields['additional_comments'].initial = self.instance.partnership.additional_comments
            self.fields['representitive'].initial = self.instance.partnership.representitive
            self.fields['vat_number'].initial = self.instance.partnership.vat_number
            self.fields['gst_number'].initial = self.instance.partnership.gst_number
            self.fields['tax_id_number'].initial = self.instance.partnership.tax_id_number
            self.fields['d_and_b_number'].initial = self.instance.partnership.d_and_b_number
            
    def clean_email(self):
        if not self.cleaned_data['email'].strip() == self.old_email.strip() and User.objects.filter(email__iexact=self.cleaned_data['email'].strip()):
            raise forms.ValidationError('This email address already has an account with us.')

        return self.cleaned_data['email'].strip()
        
    def save(self, *args, **kwargs):
        obj = super(MyProfileForm, self).save(*args, **kwargs)
        
        if obj.is_partner:
            if self.cleaned_data['num_branches']:
                obj.partnership.num_branches = self.cleaned_data['num_branches']
                
            if self.cleaned_data['branch_offices']:
                obj.partnership.branch_offices = self.cleaned_data['branch_offices']
                
            if self.cleaned_data['countries_requesting_to_sell_in']:
                obj.partnership.countries_requesting_to_sell_in = self.cleaned_data['countries_requesting_to_sell_in']
                
            if self.cleaned_data['us_states_requesting_to_sell_in']:
                obj.partnership.us_states_requesting_to_sell_in = self.cleaned_data['us_states_requesting_to_sell_in']
                
            if self.cleaned_data['annual_revenue']:
                obj.partnership.annual_revenue = self.cleaned_data['annual_revenue']
                
            if self.cleaned_data['years_in_business']:
                obj.partnership.years_in_business = self.cleaned_data['years_in_business']
                
            if self.cleaned_data['num_sales_reps']:
                obj.partnership.num_sales_reps = self.cleaned_data['num_sales_reps']
                
            if self.cleaned_data['num_systems_engineers']:
                obj.partnership.num_systems_engineers = self.cleaned_data['num_systems_engineers']
                
            if self.cleaned_data['num_technical_support_staff']:
                obj.partnership.num_technical_support_staff = self.cleaned_data['num_technical_support_staff']
                
            if self.cleaned_data['business_type']:
                obj.partnership.business_type = self.cleaned_data['business_type']
                
            if self.cleaned_data['preferred_distributor']:
                obj.partnership.preferred_distributor = self.cleaned_data['preferred_distributor']
                
            if self.cleaned_data['target_vertical_focus']:
                obj.partnership.target_vertical_focus = self.cleaned_data['target_vertical_focus']
                
            if self.cleaned_data['resell_to_usa_federal_sectors']:
                obj.partnership.resell_to_usa_federal_sectors = self.cleaned_data['resell_to_usa_federal_sectors']
                
            if self.cleaned_data['offer_own_support']:
                obj.partnership.offer_own_support = self.cleaned_data['offer_own_support']
                
            if self.cleaned_data['manufacturers_selling']:
                obj.partnership.manufacturers_selling = self.cleaned_data['manufacturers_selling']
                
            if self.cleaned_data['leading_competitors']:
                obj.partnership.leading_competitors = self.cleaned_data['leading_competitors']
                
            if self.cleaned_data['additional_comments']:
                obj.partnership.additional_comments = self.cleaned_data['additional_comments']
                
            if self.cleaned_data['representitive']:
                obj.partnership.representitive = self.cleaned_data['representitive']
                
            if self.cleaned_data['vat_number']:
                obj.partnership.vat_number = self.cleaned_data['vat_number']
                
            if self.cleaned_data['gst_number']:
                obj.partnership.gst_number = self.cleaned_data['gst_number']
                
            if self.cleaned_data['tax_id_number']:
                obj.partnership.tax_id_number = self.cleaned_data['tax_id_number']
                
            if self.cleaned_data['d_and_b_number']:
                obj.partnership.d_and_b_number = self.cleaned_data['d_and_b_number']
            
            obj.partnership.save()
            
        return obj
    
class CompleteMyProfileForm(MyProfileForm):
    class Meta(MyProfileForm.Meta):
        fields = ('mobile_number', 'address', 'city', 'state_province', 'country',
                  'company', 'job_title', 'industry', 'num_employees', 'requests_or_comments',
                  'heard_about_from', 'website')
        
    def __init__(self, *args, **kwargs):
        super(MyProfileForm, self).__init__(*args, **kwargs)
        
class NewsletterSignupForm(forms.Form):
    newsletter_email = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        super(NewsletterSignupForm, self).__init__(*args, **kwargs)

        self.user = None
        self.request = kwargs['initial'].get('request')

        if kwargs['initial'].has_key('user') and kwargs['initial']['user'].is_authenticated():
            self.user = kwargs['initial']['user']

        self.fields['newsletter_email'].widget.attrs.update({'class': 'required email'})

    def clean_email(self):
        if self.user is not None:
            if not self.user.is_authenticated() and User.objects.filter(email__iexact=self.cleaned_data['newsletter_email']):
                raise forms.ValidationError('This email address already has an account with us. Please log in to complete this request.')

        return self.cleaned_data['newsletter_email']

    def save(self):
        if self.user is not None:
            self.user.profile.newsletter_recipient = True
            self.user.profile.save()
        else:
            try:
                profile = models.Profile.objects.get(email=self.cleaned_data['newsletter_email'])
                profile.newsletter_recipient = True
                profile.save()
            except models.Profile.DoesNotExist:
                profile = models.SkyHighRegistrationProfile.objects.create_inactive_profile(site=Site.objects.get_current(),
                    request=self.request,
                    send_email=False,
                    email=self.cleaned_data['newsletter_email'],
                    first_name='',
                    last_name='',
                    company='',
                    job_title='',
                    phone_number='',
                    newsletter_recipient=True
                )

class CompleteUserProfileForm(forms.Form, CleanPasswordMixin, CleanEmailExistingMixin):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=75)
    company = forms.CharField(max_length=128, required=False)
    job_title = forms.CharField(max_length=32, required=False)
    password1 = forms.CharField(max_length=32, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=32, widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(CompleteUserProfileForm, self).__init__(*args, **kwargs)

        self.user = None
        if kwargs['initial'].has_key('email'):
            try:
                self.user = User.objects.get(email=kwargs['initial']['email'])
                self.fields['first_name'].initial = self.user.profile.first_name
                self.fields['last_name'].initial = self.user.profile.last_name

                self.fields['email'].initial = self.user.profile.email
                self.fields['email'].widget.attrs.update({'readonly':'readonly'})

                if self.user.profile.company:
                    self.fields['company'].initial = self.user.profile.company
                    self.fields['company'].widget.attrs.update({'readonly':'readonly'})

                if self.user.profile.job_title:
                    self.fields['job_title'].initial = self.user.profile.job_title
                    self.fields['job_title'].widget.attrs.update({'readonly':'readonly'})
            except User.DoesNotExist:
                pass

        self.fields['password1'].widget.attrs.update({'required': 'required'})
        self.fields['password2'].widget.attrs.update({'required': 'required'})

    def save(self):
        try:
            profile = models.Profile.objects.get(email=self.cleaned_data['email'], is_active=False)

            if self.cleaned_data['first_name']:
                profile.first_name = self.cleaned_data['first_name']

            if self.cleaned_data['last_name']:
                profile.last_name = self.cleaned_data['last_name']

            if self.cleaned_data['company']:
                profile.company = self.cleaned_data['company']

            if self.cleaned_data['job_title']:
                profile.job_title = self.cleaned_data['job_title']

            profile.set_password(self.cleaned_data['password1'])

            profile.save()

            registration_profile = models.SkyHighRegistrationProfile.objects.get(user=profile.user)
            automatic_emails.email_account_activation.delay(registration_profile.id, Site.objects.get_current().id)
        except models.Profile.DoesNotExist:
            pass

class CSPAttributeForm(forms.Form):
    csp_relation_id = forms.CharField(widget=forms.HiddenInput, required=False)
    csp_attribute = forms.ModelChoiceField(queryset=models.CSPAttribute.objects.all())
    value = forms.CharField(max_length=250)

    def save(self, *args, **kwargs):
        if self.cleaned_data.has_key('csp_relation_id') and self.cleaned_data.has_key('csp_attribute') and self.cleaned_data.has_key('value'):
            if self.cleaned_data['csp_relation_id']:
                csp_attribute_relation = models.CSPAttributeThrough.objects.get(
                    pk=self.cleaned_data['csp_relation_id'])

                csp_attribute_relation.cloud_service_provider_attribute = self.cleaned_data['csp_attribute']
                csp_attribute_relation.value = self.cleaned_data['value']
                csp_attribute_relation.save()
            else:
                profile = kwargs.get('profile')

                if profile is not None:
                    models.CSPAttributeThrough.objects.create(cloud_service_provider=models.CloudServiceProvider.objects.get(partnership=profile.partnership),
                        cloud_service_provider_attribute=self.cleaned_data['csp_attribute'], value=self.cleaned_data['value'])

CSPAttributeFormSet = formset_factory(CSPAttributeForm)

class MyProfileCSPAttributesForm(forms.Form):

    def fill_initial_value(self, field, si_number):
        if self.user is not None and self.user.profile.is_cloud_service_provider:
                try:
                    csp_relation = models.CSPAttributeThrough.objects.get(cloud_service_provider=self.user.profile.cloud_service_provider,
                        cloud_service_provider_attribute__si_number=si_number)

                    if hasattr(self.fields[field], '_queryset'):
                        self.fields[field].initial = csp_relation.cloud_service_provider_attribute.options.get(name=csp_relation.value)
                    else:
                        self.fields[field].initial = csp_relation.value

                except models.CSPAttributeThrough.DoesNotExist:
                    pass

    def save_current_value(self, field, si_number):
        if self.user is not None and self.user.profile.is_cloud_service_provider:
            if self.cleaned_data[field] is not None:
                if hasattr(self.fields[field], '_queryset'):
                    value = self.cleaned_data[field].name
                else:
                    value = self.cleaned_data[field]

                attribute, created = models.CSPAttributeThrough.objects.get_or_create(cloud_service_provider=self.user.profile.cloud_service_provider,
                    cloud_service_provider_attribute=models.CSPAttribute.objects.get(si_number=si_number),defaults={'value': value})

                if not created:
                    attribute.value = value
                    attribute.save()

    def __init__(self, *args, **kwargs):
        super(MyProfileCSPAttributesForm, self).__init__(*args, **kwargs)

        self.user = self.initial.get('user')

    def save(self):
        if self.user is not None:
            if self.user.profile.csp_attributes:
                num_csp_attributes = models.CSPAttribute.objects.count()
                csp_rels = models.CSPAttributeThrough.objects.filter(cloud_service_provider__partnership__user=self.user)

                if csp_rels.count() == num_csp_attributes:
                    if all(i.value for i in csp_rels):
                        automatic_emails.email_csp_attributes_updated.delay(self.user.id)

class MyProfileCSPAttributesDataForm(MyProfileCSPAttributesForm):
    data_sharing_support = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=1))
    data_capacity = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=2))
    data_encryption_at_rest = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=3))
    data_encryption_in_transit = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=4))
    data_multi_tenancy = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=5))
    data_mingling = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=6))
    data_retention_on_termination = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=7))
    auto_sync_data = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=8))
    encryption_strength = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=9))
    password_policy_strength = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=10))

    def __init__(self, *args, **kwargs):
        super(MyProfileCSPAttributesDataForm, self).__init__(*args, **kwargs)

        for i, key in enumerate(self.fields.iterkeys()):
            self.fill_initial_value(key, i+1)

    def save(self):
        for i, key in enumerate(self.fields.iterkeys()):
            self.save_current_value(key, i+1)

        super(MyProfileCSPAttributesDataForm, self).save()

class MyProfileCSPAttributesUserDeviceForm(MyProfileCSPAttributesForm):
    anonymous_use = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=11))
    multi_factor_authentication = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=12))
    jail_broken_app = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=13))
    mobile_app_support = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=14))
    identity_federation_method = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=15))
    enterprise_identity = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=16))
    sso = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=17))

    def __init__(self, *args, **kwargs):
        super(MyProfileCSPAttributesUserDeviceForm, self).__init__(*args, **kwargs)

        for i, key in enumerate(self.fields.iterkeys()):
            self.fill_initial_value(key, i+11)

    def save(self):
        for i, key in enumerate(self.fields.iterkeys()):
            self.save_current_value(key, i+11)

        super(MyProfileCSPAttributesUserDeviceForm, self).save()

class MyProfileCSPAttributesServiceForm(MyProfileCSPAttributesForm):
    recent_vulnerabilities = forms.CharField(max_length=500)
    csrf = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=19))
    sqli = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=20))
    xss = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=21))
    pentesting = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=22))
    api_supported = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=23))
    api_url = forms.URLField(max_length=250)
    ip_filtering_support = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=25))
    malware_site_use = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=26))
    api_authentication = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=27))

    def __init__(self, *args, **kwargs):
        super(MyProfileCSPAttributesServiceForm, self).__init__(*args, **kwargs)

        for i, key in enumerate(self.fields.iterkeys()):
            self.fill_initial_value(key, i+18)

    def save(self):
        for i, key in enumerate(self.fields.iterkeys()):
            self.save_current_value(key, i+18)

        super(MyProfileCSPAttributesServiceForm, self).save()

class MyProfileCSPAttributesBusinessRiskForm(MyProfileCSPAttributesForm):
    service_hosting_locations = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=28))
    compliance_certifications = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=29))
    service_address = forms.CharField(max_length=3000)
    pricing_model = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=31))
    price = forms.CharField(max_length=250)
    infrastructure_status_reporting = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=33))
    business_hq = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=34))
    admin_audit_logging = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=35))
    user_activity_logging = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=36))
    data_access_logging = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=37))

    def __init__(self, *args, **kwargs):
        super(MyProfileCSPAttributesBusinessRiskForm, self).__init__(*args, **kwargs)

        for i, key in enumerate(self.fields.iterkeys()):
            self.fill_initial_value(key, i+28)

    def save(self):
        for i, key in enumerate(self.fields.iterkeys()):
            self.save_current_value(key, i+28)

        super(MyProfileCSPAttributesBusinessRiskForm, self).save()

class MyProfileCSPAttributesLegalForm(MyProfileCSPAttributesForm):
    terms_of_use = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=38))
    data_residency = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=39))
    service_not_in_itar_list = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=40))
    account_termination = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=41))
    ip_ownership = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=42))
    privacy_policy = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=43))
    impacted_by_compliance = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=44))
    dispute_resolution = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=45))
    jurisdictional_location = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=46))
    indemnity = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=47))
    copyright_controls = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=48))
    statute_of_limitations = forms.ModelChoiceField(queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=49))

    def __init__(self, *args, **kwargs):
        super(MyProfileCSPAttributesLegalForm, self).__init__(*args, **kwargs)

        for i, key in enumerate(self.fields.iterkeys()):
            self.fill_initial_value(key, i+38)

    def save(self):
        for i, key in enumerate(self.fields.iterkeys()):
            self.save_current_value(key, i+38)

        super(MyProfileCSPAttributesLegalForm, self).save()
        
class SFTPAccount(forms.ModelForm):
    password_repeat = forms.CharField()
    
    class Meta:
        model = models.SFTPUser
        fields = ['username', 'password', 'password_repeat']
        
    def clean_password(self):
        """
        Verify password is strong and matches criteria

        """
        if 'password' in self.cleaned_data:
            PWD_MIN_CHAR = 8
            PWD_MAX_CHAR = 45

            pattern = "(?=^.{%i,%i}$)((?=.*\\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^A-Za-z0-9]))^.*" % (PWD_MIN_CHAR, PWD_MAX_CHAR)

            if re.match(pattern, self.cleaned_data['password']) is None:
                raise forms.ValidationError('Valid password should contain at least %i alphanumeric characters. Contain both upper and lower case letters. Contain at least one number (for example, 0-9). Contain at least one special character (for example,!@#$%%^&*()+=-[]\\\';,./{}|\":?~_<>)' % PWD_MIN_CHAR)

        return self.cleaned_data['password']

    def clean_password_repeat(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        if 'password' in self.cleaned_data and 'password_repeat' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['password_repeat']:
                raise forms.ValidationError('The password fields didn\'t match: Password confirmation failed.')
        return self.cleaned_data['password_repeat']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        if 'password' in self.cleaned_data and 'password_repeat' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['password_repeat']:
                raise forms.ValidationError('The two password fields didn\'t match.')
        return self.cleaned_data
        
    def __init__(self, *args, **kwargs):
        super(SFTPAccount, self).__init__(*args, **kwargs)