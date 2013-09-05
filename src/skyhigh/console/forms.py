'''
Created on 10 Jan 2013

@author: euan
'''
import hashlib
import csv
import re
import pytz

from django import forms
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib.auth.models import User as TheUserClass
from django.utils import timezone
from django.contrib import messages

from skyhigh import models, constants, utils, automatic_emails

from skyhigh.console import fields

from unobase.forms import Content
from unobase import utils as unobase_utils

from ckeditor.widgets import CKEditorWidget

from flufl.password import generate

class Event(Content):
    image_choice = forms.ChoiceField(choices=(('new', 'new'), ('existing', 'existing')))
    existing_image = fields.ImageModelChoiceField(required=False,
        queryset=models.Event.objects.filter(~Q(image=None)).only('image', 'image_name').distinct())

    class Meta(Content.Meta):
        model = models.Event
        fields = Content.Meta.fields + ['start_date', 'start_time', 'end_date', 'end_time', 'external_link', 'image_name']

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)

        self.fields['start_time'].required = False
        self.fields['end_date'].required = False
        self.fields['end_time'].required = False

        if self.fields['existing_image']._queryset:
            self.existing_images = True
        else:
            self.existing_images = False

        self.fields['existing_image'].widget.attrs.update({'data-content-type': 'event'})

    def save(self, *args, **kwargs):
        obj = super(Event, self).save(*args, **kwargs)

        if self.cleaned_data['image_choice'] == 'existing':
            if self.cleaned_data['existing_image'] is not None:
                obj.image = self.cleaned_data['existing_image'].image
                obj.save()

        return obj

class MediaCoverage(Content):
    image_choice = forms.ChoiceField(choices=(('new', 'new'), ('existing', 'existing')))
    existing_image = fields.ImageModelChoiceField(required=False,
        queryset=models.MediaCoverage.objects.filter(~Q(image=None)).only('image', 'image_name').distinct())

    class Meta(Content.Meta):
        model = models.MediaCoverage
        fields = Content.Meta.fields + ['pdf', 'external_link', 'image_name']

    def __init__(self, *args, **kwargs):
        super(MediaCoverage, self).__init__(*args, **kwargs)

        if self.fields['existing_image']._queryset:
            self.existing_images = True
        else:
            self.existing_images = False

        self.fields['existing_image'].widget.attrs.update({'data-content-type': 'media_coverage'})

    def save(self, *args, **kwargs):
        obj = super(MediaCoverage, self).save(*args, **kwargs)

        if self.cleaned_data['image_choice'] == 'existing':
            if self.cleaned_data['existing_image'] is not None:
                obj.image = self.cleaned_data['existing_image'].image
                obj.save()

        return obj

class PressRelease(Content):
    class Meta(Content.Meta):
        model = models.PressRelease
        fields = Content.Meta.fields + ['pdf']

class CareerForm(Content):
    class Meta(Content.Meta):
        model = models.Career
        fields = Content.Meta.fields + ['position']
        
class Leadership(Content):
    class Meta(Content.Meta):
        model = models.Leader
        
class Investor(Content):
    class Meta(Content.Meta):
        model = models.Investor
        
class CaseStudy(Content):
    class Meta(Content.Meta):
        model = models.CaseStudy
        fields = Content.Meta.fields + ['has_detail', 'pdf']
        
class ConfigurableEmail(forms.ModelForm):
    class Meta:
        model = models.ConfigurableEmail
        fields = ['title', 'subject', 'content', 'plaintext_content',
                  'internal_bccs']
        
    def __init__(self, *args, **kwargs):
        super(ConfigurableEmail, self).__init__(*args, **kwargs)
        
        self.fields['title'].widget.attrs.update({'readonly': 'readonly'})
        self.fields['internal_bccs'].widget.attrs.update({'class': 'chzn_select'})
        
class SFTPUser(forms.ModelForm):
    password_repeat = forms.CharField()
    
    class Meta:
        model = models.SFTPUser

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
        super(SFTPUser, self).__init__(*args, **kwargs)
        
        self.fields['user'].queryset = TheUserClass.objects.all().order_by('email')
        self.fields['user'].widget.attrs.update({'class': 'chzn_select'})
        
class SFTPUserFilter(forms.Form):
    username = forms.CharField(required=False)

class User(forms.ModelForm):
    default_image = forms.BooleanField(initial=False, required=False)

    class Meta:
        model = models.Profile

        fields = ['title', 'image', 'first_name', 'last_name', 'email', 'company', 'job_title',
                  'phone_number', 'mobile_number', 'address', 'city', 'zip_postal_code',
                  'state_province', 'country', 'timezone', 'role']

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        self.object = kwargs['instance']

        self.fields['image'].required = False

    def save(self, *args, **kwargs):
        obj = super(User, self).save(*args, **kwargs)
        if self.cleaned_data.has_key('default_image') and self.cleaned_data['default_image']:
            obj.image = None
            obj.save()

        return obj
    
class PendingEvaluatorFilter(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.CharField(required=False)

class UserFilter(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.CharField(required=False)
    company = forms.CharField(required=False)
    job_title = forms.CharField(required=False)


class Partner(User):
    partnership_status = forms.ChoiceField(choices=constants.PARTNERSHIP_REQUEST_STATUS_CHOICES)
    partner_type = forms.ChoiceField(choices=constants.PARTNER_TYPE_CHOICES)
    technology_partner_subtype = forms.BooleanField(required=False)
    technology_partner_subtype_category = forms.ChoiceField(choices=constants.CSP_CATEGORY_CHOICES, required=False)
    technology_partner_subtype_url = forms.URLField(required=False)
    channel_partner_subtype = forms.ChoiceField(choices=constants.CHANNEL_PARTNER_TYPE_CHOICES,
        initial=constants.CHANNEL_PARTNER_TYPE_RESELLER, widget=forms.RadioSelect(), required=False)

    def __init__(self, *args, **kwargs):
        super(Partner, self).__init__(*args, **kwargs)

        if self.object is not None:
            try:
                partnership = models.Partnership.objects.get(user=self.object)
                partner_type = partnership.type
                self.fields['partnership_status'].initial = partnership.status
                self.fields['partner_type'].initial = partner_type

                if partner_type == constants.PARTNER_TYPE_TECHNOLOGY:
                    try:
                        if partnership.cloud_service_provider:
                            self.fields['technology_partner_subtype'].initial = True
                            self.fields['technology_partner_subtype_category'].initial = partnership.cloud_service_provider.category
                            self.fields['technology_partner_subtype_url'].initial = partnership.cloud_service_provider.url
                    except models.CloudServiceProvider.DoesNotExist:
                        pass

                elif partner_type == constants.PARTNER_TYPE_CHANNEL:
                    try:
                        if partnership.reseller:
                            self.fields['channel_partner_subtype'].initial = constants.CHANNEL_PARTNER_TYPE_RESELLER
                    except models.Reseller.DoesNotExist:
                        pass

                    try:
                        if partnership.distributor:
                            self.fields['channel_partner_subtype'].initial = constants.CHANNEL_PARTNER_TYPE_DISTRIBUTOR
                    except models.Distributor.DoesNotExist:
                        pass

            except models.Partnership.DoesNotExist:
                pass

        else:
            partner_type = self.initial['type']

            if partner_type == 'technical':
                self.fields['partner_type'].initial = constants.PARTNER_TYPE_TECHNOLOGY
            elif partner_type == 'channel':
                self.fields['partner_type'].initial = constants.PARTNER_TYPE_CHANNEL


    def save(self, *args, **kwargs):
        obj = super(Partner, self).save(*args, **kwargs)

        if self.cleaned_data.has_key('partnership_status') and self.cleaned_data.has_key('partner_type'):
            partnership_status = self.cleaned_data['partnership_status']
            partner_type = int(self.cleaned_data['partner_type'])

            partnership, created = models.Partnership.objects.get_or_create(
                user=obj, defaults={'status': partnership_status,
                                    'type': partner_type}
            )

            if not created:
                partnership.status = self.cleaned_data['partnership_status']
                partnership.type = self.cleaned_data['partner_type']
                partnership.save()

            if partner_type == constants.PARTNER_TYPE_TECHNOLOGY:
                try:
                    distributor = models.Distributor.objects.get(partnership=partnership).delete()
                except models.Distributor.DoesNotExist:
                    pass

                try:
                    reseller = models.Reseller.objects.get(partnership=partnership).delete()
                except models.Reseller.DoesNotExist:
                    pass

                if self.cleaned_data.has_key('technology_partner_subtype'):
                    if self.cleaned_data['technology_partner_subtype']:
                        csp, created = models.CloudServiceProvider.objects.get_or_create(partnership=partnership, defaults={
                            'category': self.cleaned_data['technology_partner_subtype_category'],
                            'url': self.cleaned_data['technology_partner_subtype_url']
                        })

                        if not created:
                            csp.category = self.cleaned_data['technology_partner_subtype_category']
                            csp.url = self.cleaned_data['technology_partner_subtype_url']
                            csp.save()

            elif partner_type == constants.PARTNER_TYPE_CHANNEL:
                try:
                    models.CloudServiceProvider.objects.get(partnership=partnership).delete()
                except models.CloudServiceProvider.DoesNotExist:
                    pass

                if self.cleaned_data.has_key('channel_partner_subtype'):
                    if int(self.cleaned_data['channel_partner_subtype']) == constants.CHANNEL_PARTNER_TYPE_DISTRIBUTOR:
                        try:
                            reseller = models.Reseller.objects.get(partnership=partnership).delete()
                        except models.Reseller.DoesNotExist:
                            pass

                        distributor, _ = models.Distributor.objects.get_or_create(partnership=partnership)
                    elif int(self.cleaned_data['channel_partner_subtype']) == constants.CHANNEL_PARTNER_TYPE_RESELLER:
                        try:
                            distributor = models.Distributor.objects.get(partnership=partnership).delete()
                        except models.Distributor.DoesNotExist:
                            pass

                        reseller, _ = models.Reseller.objects.get_or_create(partnership=partnership)

        return obj

class Evaluator(User):
    evaluator_status = forms.ChoiceField(choices=constants.PRODUCT_EVALUATION_STATUS_CHOICES)

    def __init__(self, *args, **kwargs):
        super(Evaluator, self).__init__(*args, **kwargs)

        if self.object is not None:
            try:
                product_evaluation = models.ProductEvaluation.objects.get(user=self.object)
                self.fields['evaluator_status'].initial = product_evaluation.status
            except models.ProductEvaluation.DoesNotExist:
                pass


    def save(self, *args, **kwargs):
        obj = super(Evaluator, self).save(*args, **kwargs)

        if self.cleaned_data.has_key('evaluator_status'):
            product_evaluation, created = models.ProductEvaluation.objects.get_or_create(
                user=obj, defaults={'status': self.cleaned_data['evaluator_status']}
            )

            if not created:
                product_evaluation.status = self.cleaned_data['evaluator_status']
                product_evaluation.save()

        return obj

class ExistingUserEvaluator(Evaluator):

    class Meta:
        model = models.Profile

        fields = ['image', 'title', 'first_name', 'last_name', 'email', 'company', 'job_title']

    def __init__(self, *args, **kwargs):
        super(Evaluator, self).__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs.update({'readonly': 'readonly'})
        self.fields['last_name'].widget.attrs.update({'readonly': 'readonly'})
        self.fields['email'].widget.attrs.update({'readonly': 'readonly'})
        self.fields['company'].widget.attrs.update({'readonly': 'readonly'})
        self.fields['job_title'].widget.attrs.update({'readonly': 'readonly'})

class UserImport(forms.Form):
    """
    Form accepting and validating CSV file, returning collection of validated
    dictionaries to import.
    """
    duplicate_file_reimport = forms.BooleanField(
        required=False,
        widget=forms.HiddenInput()
    )
    create = forms.BooleanField(
        label='Create New Users',
        help_text='Users that exist in the import, but not in SkyhighNetworks will always '
                  'be created.',
        required=False
    )
    update = forms.BooleanField(
        label='Update Existing Users',
        help_text='Update existing users with the attributes specified in the '
                  'import data.',
        required=False
    )
    source = forms.FileField(
        label='Select the CSV File to Import'
    )
    email = forms.BooleanField(
        label='',
        help_text='Send an email to all users who get created without a '
                  'password being provided in the import data.',
        required=False
    )

    def clean_source(self):
        uploaded_file = self.cleaned_data['source']
        md5 = hashlib.md5(uploaded_file.read()).hexdigest()
        if not self.cleaned_data['duplicate_file_reimport']:
            try:
                models.UserImportHash.objects.get(md5=md5)
                self.data['duplicate_file_reimport'] = u'on'
                raise forms.ValidationError(
                    "%s appears to have been imported previously. If you "
                    "want to re-import it please specify it again and "
                    "click import. Note: this might cause data "
                    "duplication." % uploaded_file.name
                )
            except models.UserImportHash.DoesNotExist:
                pass
        uploaded_file.seek(0)
        reader = csv.reader(uploaded_file, delimiter=',')
        valid_rows = []
        usernames = []
        for i, row in enumerate(reader):
            if i == 0:
                keys = row
            else:
                data = {}
                for j, value in enumerate(row):
                    data[keys[j]] = value
                csv_form = UserCSVRowForm(data, initial={'update': self.cleaned_data['update']})
                if csv_form.is_valid():
                    data = csv_form.cleaned_data

                    valid_rows.append(data)
                    if data['email'] in usernames:
                        raise forms.ValidationError(
                            'Username "%s" appears multiple times in your '
                            'CSV data. Please ensure usernames are unique.'
                            % data['email']
                        )
                    else:
                        usernames.append(data['email'])
                else:
                    csv_errors = []
                    for key, value in csv_form.errors.items():
                        csv_errors.append(
                            '%s value of "%s" is invalid (row %s). %s'
                            % (key, data[key], i, value[0])
                        )
                    raise forms.ValidationError(csv_errors)
        models.UserImportHash.objects.get_or_create(md5=md5)
        return valid_rows

    def save(self, request, *args, **kwargs):
        update_count = 0
        create_count = 0

        for obj in self.cleaned_data['source']:
            created = False
            try:
                user = models.Profile.objects.get(username=obj['email'])
            except models.Profile.DoesNotExist:
                user = None

            if user is None and self.cleaned_data['create']:
                user = models.Profile.objects.create(
                    username=obj['email'],
                    email=obj['email']
                )
                password = generate(10)
                user.set_password(password)
                created = True
                create_count += 1

            if created or self.cleaned_data['update']:
                # Set simple fields.
                if obj['address']:
                    user.address = obj['address']
                if obj['city']:
                    user.city = obj['city']
                if obj['first_name']:
                    user.first_name = obj['first_name']
                if obj['job_title']:
                    user.job_title = obj['job_title']
                if obj['last_name']:
                    user.last_name = obj['last_name']
                if obj['mobile_number']:
                    user.mobile_number = obj['mobile_number']
                if obj['phone_number']:
                    user.phone_number = obj['phone_number']
                if obj['timezone']:
                    user.timezone = obj['timezone']
                if obj['zip_postal_code']:
                    user.zip_postal_code = obj['zip_postal_code']
                    # Ensure user is published/not 'deleted'.

                # Set complex fields.
                if obj['country']:
                    user.country = models.Country.objects.get_or_create(name=obj['country'])[0]

                user.save()

                if obj['evaluator']:
                    product_evaluation, created = models.ProductEvaluation.objects.get_or_create(user=user.user,
                        defaults={'status': constants.PRODUCT_EVALUATION_STATUS_APPROVED})

                    if not created:
                        product_evaluation.status = constants.PRODUCT_EVALUATION_STATUS_APPROVED
                        product_evaluation.save()

                if obj['channel_partner']:
                    partnership, created = models.Partnership.objects.get_or_create(user=user.user,
                        type=constants.PARTNER_TYPE_CHANNEL,
                        defaults={'status': constants.PARTNERSHIP_REQUEST_STATUS_APPROVED})

                    if not created:
                        partnership.status = constants.PARTNERSHIP_REQUEST_STATUS_APPROVED
                        partnership.save()

                    if object['distributor']:
                        distributor, _ = models.Distributor.objects.get_or_create(partnership=partnership)
                    elif object['reseller']:
                        reseller, _ = models.Reseller.objects.get_or_create(partnership=partnership)

                elif obj['technical_partner']:
                    partnership, created = models.Partnership.objects.get_or_create(user=user.user,
                        type=constants.PARTNER_TYPE_TECHNOLOGY,
                        defaults={'status': constants.PARTNERSHIP_REQUEST_STATUS_APPROVED})

                    if not created:
                        partnership.status = constants.PARTNERSHIP_REQUEST_STATUS_APPROVED
                        partnership.save()

                    if obj['cloud_service_provider']:
                        cloud_service_provider, _ = models.CloudServiceProvider.objects.get_or_create(partnership=partnership)

                if not created:
                    update_count += 1

            if created:
                if self.cleaned_data['email'] and obj['email']:
                    automatic_emails.email_successful_account_activation.delay(user.user.id)

        messages.success(
            request,
            "Thank you! Your import completed successfully."
        )

class UserCSVRowForm(forms.Form):
    """
    Form to validate individual CSV rows.
    """
    email = forms.EmailField()
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    phone_number = forms.CharField(required=False)
    mobile_number = forms.CharField(required=False)
    address = forms.CharField(max_length=512, required=False)
    city = forms.CharField(max_length=32, required=False)
    zip_postal_code = forms.CharField(max_length=8, required=False)
    state_province = forms.CharField(max_length=100, required=False)
    country = forms.CharField(max_length=100, required=False)
    job_title = forms.CharField(max_length=22, required=False)
    timezone = forms.CharField(max_length=64, required=False)
    evaluator = forms.BooleanField(required=False)
    channel_partner = forms.BooleanField(required=False)
    distributor = forms.BooleanField(required=False)
    reseller = forms.BooleanField(required=False)
    technical_partner = forms.BooleanField(required=False)
    cloud_service_provider = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(UserCSVRowForm, self).__init__(*args, **kwargs)

        self.update = self.initial.get('update')

    def clean_timezone(self):
        value = self.cleaned_data['timezone']
        if not value:
            return value
        if value not in pytz.common_timezones:
            raise forms.ValidationError("")

    def validate_phone_number(self, field_name):
        value = self.cleaned_data[field_name]
        if not value:
            return value

        if not re.match("^\d{11}$", value):
            raise forms.ValidationError(
                "Please provide a valid eleven digit number."
            )
        return value

    def clean_mobile_number(self):
        return self.validate_phone_number('mobile_number')

    def clean_phone_number(self):
        return self.validate_phone_number('phone_number')

    def clean_email(self):
        if not self.update:
            try:
                TheUserClass.objects.get(email=self.cleaned_data['email'])
                raise forms.ValidationError('Email address already exists')
            except TheUserClass.DoesNotExist:
                pass

        return self.cleaned_data['email']

class CSPImport(forms.Form):
    """
    Form accepting and validating CSV file, returning collection of validated
    dictionaries to import.
    """
    duplicate_file_reimport = forms.BooleanField(
        required=False,
        widget=forms.HiddenInput()
    )
    create = forms.BooleanField(
        label='Create New CSPs',
        help_text='CSPs that exist in the import, but not in SkyhighNetworks will always '
                  'be created.',
        required=False
    )
    update = forms.BooleanField(
        label='Update Existing CSPs',
        help_text='Update existing CSPs with the attributes specified in the '
                  'import data.',
        required=False
    )
    source = forms.FileField(
        label='Select the CSV File to Import'
    )
    email = forms.BooleanField(
        label='',
        help_text='Send an email to all CSPs who get created without a '
                  'password being provided in the import data.',
        required=False
    )

    def clean_source(self):
        uploaded_file = self.cleaned_data['source']
        md5 = hashlib.md5(uploaded_file.read()).hexdigest()
        if not self.cleaned_data['duplicate_file_reimport']:
            try:
                models.UserImportHash.objects.get(md5=md5)
                self.data['duplicate_file_reimport'] = u'on'
                raise forms.ValidationError(
                    "%s appears to have been imported previously. If you "
                    "want to re-import it please specify it again and "
                    "click import. Note: this might cause data "
                    "duplication." % uploaded_file.name
                )
            except models.UserImportHash.DoesNotExist:
                pass
        uploaded_file.seek(0)
        reader = csv.reader(uploaded_file, delimiter=',')
        valid_rows = []
        usernames = []
        for i, row in enumerate(reader):
            if i == 0:
                keys = row
            else:
                data = {}
                print row
                for j, value in enumerate(row):
                    data[keys[j]] = value
                csv_form = CSPCSVRowForm(data, initial={'update': self.cleaned_data['update']})
                if csv_form.is_valid():
                    data = csv_form.cleaned_data

                    valid_rows.append(data)
                    if data['email'] and data['email'] in usernames:
                        raise forms.ValidationError(
                            'Username "%s" appears multiple times in your '
                            'CSV data. Please ensure usernames are unique.'
                            % data['email']
                        )
                    else:
                        usernames.append(data['email'])
                else:
                    csv_errors = []
                    for key, value in csv_form.errors.items():
                        csv_errors.append(
                            '%s value of "%s" is invalid (row %s). %s'
                            % (key, data[key], i, value[0])
                        )
                    raise forms.ValidationError(csv_errors)
        models.UserImportHash.objects.get_or_create(md5=md5)
        return valid_rows

    def create_csp_attribute(self, si_number, value):
        if value == 'Yes':
            value = 'True'
        elif value == 'No':
            value = 'False'
        
        try:    
            models.CSPAttributeThrough.objects.filter(cloud_service_provider=self.cloud_service_provider,
                cloud_service_provider_attribute=models.CSPAttribute.objects.get(si_number=si_number)
            ).delete()
        except:
            pass

        models.CSPAttributeThrough.objects.create(cloud_service_provider=self.cloud_service_provider,
            cloud_service_provider_attribute=models.CSPAttribute.objects.get(si_number=si_number),
            value=value
        )

    def save(self, request, *args, **kwargs):
        update_count = 0
        create_count = 0

        for obj in self.cleaned_data['source']:
            created = False
            if obj['email']:
                try:
                    user = models.Profile.objects.get(username=obj['email'])
                except models.Profile.DoesNotExist:
                    user = None
    
                if user is None and self.cleaned_data['create']:
                    user = models.Profile.objects.create(
                        username=obj['email'],
                        email=obj['email'],
                        email_notifications=False
                    )
                    password = generate(10)
                    user.set_password(password)
                    created = True
                    create_count += 1
    
                if created or self.cleaned_data['update']:
                    # Set simple fields.
                    if obj['name']:
                        user.first_name = obj['name'][:30]
    
                    user.save()
    
                    partnership, created = models.Partnership.objects.get_or_create(user=user.user,
                        type=constants.PARTNER_TYPE_TECHNOLOGY,
                        defaults={'status': constants.PARTNERSHIP_REQUEST_STATUS_APPROVED})
    
                    if not created:
                        partnership.status = constants.PARTNERSHIP_REQUEST_STATUS_APPROVED
                        partnership.save()
    
                    self.cloud_service_provider, _ = models.CloudServiceProvider.objects.get_or_create(partnership=partnership)
    
                    if obj['url']:
                        self.cloud_service_provider.url = obj['url']
    
                    if obj['category']:
                        self.cloud_service_provider.category = unobase_utils.get_choice_value(obj['category'],
                            constants.CSP_CATEGORY_CHOICES)
    
                    if obj['csp_id']:
                        self.cloud_service_provider.csp_id = int(obj['csp_id'])
    
                    self.cloud_service_provider.save()
    
                    if obj['data_sharing_support']:
                        self.create_csp_attribute(1, obj['data_sharing_support'])
    
                    if obj['data_capacity']:
                        self.create_csp_attribute(2, obj['data_capacity'])
    
                    if obj['data_encryption_at_rest']:
                        self.create_csp_attribute(3, obj['data_encryption_at_rest'])
    
                    if obj['data_encryption_in_transit']:
                        self.create_csp_attribute(4, obj['data_encryption_in_transit'])
    
                    if obj['data_multi_tenancy']:
                        self.create_csp_attribute(5, obj['data_multi_tenancy'])
    
                    if obj['data_mingling']:
                        self.create_csp_attribute(6, obj['data_mingling'])
    
                    if obj['data_retention_on_termination']:
                        self.create_csp_attribute(7, obj['data_retention_on_termination'])
    
                    if obj['auto_sync_data']:
                        self.create_csp_attribute(8, obj['auto_sync_data'])
    
                    if obj['encryption_strength']:
                        self.create_csp_attribute(9, obj['encryption_strength'])
    
                    if obj['password_policy_strength']:
                        self.create_csp_attribute(10, obj['password_policy_strength'])
    
                    if obj['anonymous_use']:
                        self.create_csp_attribute(11, obj['anonymous_use'])
    
                    if obj['multi_factor_authentication']:
                        self.create_csp_attribute(12, obj['multi_factor_authentication'])
    
                    if obj['jail_broken_app']:
                        self.create_csp_attribute(13, obj['jail_broken_app'])
    
                    if obj['mobile_app_support']:
                        self.create_csp_attribute(14, obj['mobile_app_support'])
    
                    if obj['identity_federation_method']:
                        self.create_csp_attribute(15, obj['identity_federation_method'])
    
                    if obj['enterprise_identity']:
                        self.create_csp_attribute(16, obj['enterprise_identity'])
    
                    if obj['sso']:
                        self.create_csp_attribute(17, obj['sso'])
    
                    if obj['recent_vulnerabilities']:
                        self.create_csp_attribute(18, obj['recent_vulnerabilities'])
    
                    if obj['csrf']:
                        self.create_csp_attribute(19, obj['csrf'])
    
                    if obj['sqli']:
                        self.create_csp_attribute(20, obj['sqli'])
    
                    if obj['xss']:
                        self.create_csp_attribute(21, obj['xss'])
    
                    if obj['pentesting']:
                        self.create_csp_attribute(22, obj['pentesting'])
    
                    if obj['api_supported']:
                        self.create_csp_attribute(23, obj['api_supported'])
    
                    if obj['api_url']:
                        self.create_csp_attribute(24, obj['api_url'])
    
                    if obj['ip_filtering_support']:
                        self.create_csp_attribute(25, obj['ip_filtering_support'])
    
                    if obj['malware_site_use']:
                        self.create_csp_attribute(26, obj['malware_site_use'])
    
                    if obj['api_authentication']:
                        self.create_csp_attribute(27, obj['api_authentication'])
    
                    if obj['service_hosting_locations']:
                        self.create_csp_attribute(28, obj['service_hosting_locations'])
    
                    if obj['compliance_certifications']:
                        self.create_csp_attribute(29, obj['compliance_certifications'])
    
                    if obj['service_address']:
                        self.create_csp_attribute(30, obj['service_address'])
    
                    if obj['pricing_model']:
                        self.create_csp_attribute(31, obj['pricing_model'])
    
                    if obj['price']:
                        self.create_csp_attribute(32, obj['price'])
    
                    if obj['infrastructure_status_reporting']:
                        self.create_csp_attribute(33, obj['infrastructure_status_reporting'])
    
                    if obj['business_hq']:
                        self.create_csp_attribute(34, obj['business_hq'])
    
                    if obj['admin_audit_logging']:
                        self.create_csp_attribute(35, obj['admin_audit_logging'])
    
                    if obj['user_activity_logging']:
                        self.create_csp_attribute(36, obj['user_activity_logging'])
    
                    if obj['data_access_logging']:
                        self.create_csp_attribute(37, obj['data_access_logging'])
    
                    if obj['terms_of_use']:
                        self.create_csp_attribute(38, obj['terms_of_use'])
    
                    if obj['data_residency']:
                        self.create_csp_attribute(39, obj['data_residency'])
    
                    if obj['service_not_in_itar_list']:
                        self.create_csp_attribute(40, obj['service_not_in_itar_list'])
    
                    if obj['account_termination']:
                        self.create_csp_attribute(41, obj['account_termination'])
    
                    if obj['ip_ownership']:
                        self.create_csp_attribute(42, obj['ip_ownership'])
    
                    if obj['privacy_policy']:
                        self.create_csp_attribute(43, obj['privacy_policy'])
    
                    if obj['impacted_by_compliance']:
                        self.create_csp_attribute(44, obj['impacted_by_compliance'])
    
                    if obj['dispute_resolution']:
                        self.create_csp_attribute(45, obj['dispute_resolution'])
    
                    if obj['jurisdictional_location']:
                        self.create_csp_attribute(46, obj['jurisdictional_location'])
    
                    if obj['indemnity']:
                        self.create_csp_attribute(47, obj['indemnity'])
    
                    if obj['copyright_controls']:
                        self.create_csp_attribute(48, obj['copyright_controls'])
    
                    if obj['statute_of_limitations']:
                        self.create_csp_attribute(49, obj['statute_of_limitations'])
    
                    if not created:
                        update_count += 1

            if created:
                if self.cleaned_data['email'] and obj['email']:
                    automatic_emails.email_existing_csp_activation.delay(user.user.id)

        messages.success(
            request,
            "Thank you! Your import completed successfully."
        )

class CSPCSVRowForm(forms.Form):
    """
    Form to validate individual CSV rows.
    """
    email = forms.EmailField(required=False)
    name = forms.CharField(required=False)
    url = forms.CharField(required=False, max_length=1024)
    category = forms.CharField(required=False)
    csp_id = forms.CharField(required=False)
    data_sharing_support = forms.CharField(required=False)
    data_capacity = forms.CharField(required=False)
    data_encryption_at_rest = forms.CharField(required=False)
    data_encryption_in_transit = forms.CharField(required=False)
    data_multi_tenancy = forms.CharField(required=False)
    data_mingling = forms.CharField(required=False)
    data_retention_on_termination = forms.CharField(required=False)
    auto_sync_data = forms.CharField(required=False)
    encryption_strength = forms.CharField(required=False)
    password_policy_strength = forms.CharField(required=False)
    anonymous_use = forms.CharField(required=False)
    multi_factor_authentication = forms.CharField(required=False)
    jail_broken_app = forms.CharField(required=False)
    mobile_app_support = forms.CharField(required=False)
    identity_federation_method = forms.CharField(required=False)
    enterprise_identity = forms.CharField(required=False)
    sso = forms.CharField(required=False)
    recent_vulnerabilities = forms.CharField(required=False, max_length=500)
    csrf = forms.CharField(required=False)
    sqli = forms.CharField(required=False)
    xss = forms.CharField(required=False)
    pentesting = forms.CharField(required=False)
    api_supported = forms.CharField(required=False)
    api_url = forms.CharField(required=False, max_length=1024)
    ip_filtering_support = forms.CharField(required=False)
    malware_site_use = forms.CharField(required=False)
    api_authentication = forms.CharField(required=False)
    service_hosting_locations = forms.CharField(required=False)
    compliance_certifications = forms.CharField(required=False)
    service_address = forms.CharField(required=False, max_length=3000)
    pricing_model = forms.CharField(required=False)
    price = forms.CharField(required=False, max_length=250)
    infrastructure_status_reporting = forms.CharField(required=False)
    business_hq = forms.CharField(required=False)
    admin_audit_logging = forms.CharField(required=False)
    user_activity_logging = forms.CharField(required=False)
    data_access_logging = forms.CharField(required=False)
    terms_of_use = forms.CharField(required=False)
    data_residency = forms.CharField(required=False)
    service_not_in_itar_list = forms.CharField(required=False)
    account_termination = forms.CharField(required=False)
    ip_ownership = forms.CharField(required=False)
    privacy_policy = forms.CharField(required=False)
    impacted_by_compliance = forms.CharField(required=False)
    dispute_resolution = forms.CharField(required=False)
    jurisdictional_location = forms.CharField(required=False)
    indemnity = forms.CharField(required=False)
    copyright_controls = forms.CharField(required=False)
    statute_of_limitations = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(CSPCSVRowForm, self).__init__(*args, **kwargs)

        self.update = self.initial.get('update')


    def clean_email(self):
        if not self.update:
            try:
                TheUserClass.objects.get(email=self.cleaned_data['email'])
                raise forms.ValidationError('Email address already exists')
            except TheUserClass.DoesNotExist:
                pass

        return self.cleaned_data['email']

class ContactMessageReplyForm(forms.Form):
    from_address = forms.CharField(widget=forms.HiddenInput())
    to_address = forms.CharField(widget=forms.HiddenInput())
    message = forms.CharField(widget=CKEditorWidget)

    def __init__(self, contact_message=None, user=None, *args, **kwargs):
        super(ContactMessageReplyForm, self).__init__(*args, **kwargs)

        self.contact_message = contact_message
        self.user = user

        if self.contact_message is not None:
            self.fields['from_address'].initial = 'support@skyhighnetworks.com'
            self.fields['to_address'].initial = self.contact_message.user.email
            self.fields['message'].initial = render_to_string('skyhigh/console/messages/message_template.html', {'contact_message': self.contact_message})

    def send_mail(self):
        message = self.cleaned_data['message']
        subject = 'Skyhighnetworks.com - Response to contact'
        text_content = ''
        from_address = self.cleaned_data['from_address']
        to_addresses = [self.cleaned_data['to_address']]

        utils.send_mail(None, {}, subject, text_content, from_address, to_addresses, html_content=message)

        self.contact_message.status = constants.CONTACT_MESSAGE_STATUS_RESPONDED
        self.contact_message.modified_by = self.user
        self.contact_message.save()

class ConsoleCSPAttributesForm(forms.Form):
    si_number_1 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=1))
    si_number_2 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=2))
    si_number_3 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=3))
    si_number_4 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=4))
    si_number_5 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=5))
    si_number_6 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=6))
    si_number_7 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=7))
    si_number_8 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=8))
    si_number_9 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=9))
    si_number_10 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=10))
    si_number_11 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=11))
    si_number_12 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=12))
    si_number_13 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=13))
    si_number_14 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=14))
    si_number_15 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=15))
    si_number_16 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=16))
    si_number_17 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=17))
    si_number_18 = forms.CharField(required=False, max_length=500)
    si_number_19 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=19))
    si_number_20 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=20))
    si_number_21 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=21))
    si_number_22 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=22))
    si_number_23 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=23))
    si_number_24 = forms.URLField(required=False, max_length=250)
    si_number_25 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=25))
    si_number_26 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=26))
    si_number_27 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=27))
    si_number_28 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=28))
    si_number_29 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=29))
    si_number_30 = forms.CharField(required=False, max_length=3000)
    si_number_31 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=31))
    si_number_32 = forms.CharField(required=False, max_length=250)
    si_number_33 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=33))
    si_number_34 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=34))
    si_number_35 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=35))
    si_number_36 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=36))
    si_number_37 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=37))
    si_number_38 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=38))
    si_number_39 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=39))
    si_number_40 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=40))
    si_number_41 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=41))
    si_number_42 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=42))
    si_number_43 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=43))
    si_number_44 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=44))
    si_number_45 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=45))
    si_number_46 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=46))
    si_number_47 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=47))
    si_number_48 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=48))
    si_number_49 = forms.ModelChoiceField(required=False, queryset=models.CSPAttributeOption.objects.filter(attribute__si_number=49))

    def __init__(self, *args, **kwargs):
        super(ConsoleCSPAttributesForm, self).__init__(*args, **kwargs)

        self.profile = self.initial.get('profile')

    def save_current_value(self, field, si_number):
        if self.profile is not None and self.profile.is_cloud_service_provider:
            if self.cleaned_data[field] is not None:
                if hasattr(self.fields[field], '_queryset'):
                    value = self.cleaned_data[field].name
                else:
                    value = self.cleaned_data[field]

                attribute, created = models.CSPAttributeThrough.objects.get_or_create(cloud_service_provider=self.profile.cloud_service_provider,
                    cloud_service_provider_attribute=models.CSPAttribute.objects.get(si_number=si_number),defaults={'value': value})

                if not created:
                    attribute.value = value
                    attribute.save()

    def save(self):
        for i, key in enumerate(self.fields.iterkeys()):
            self.save_current_value(key, i+1)

