'''
Created on 29 Dec 2012

@author: euan
'''
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils.encoding import smart_unicode
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.validators import MaxLengthValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify

from flufl.password import generate

from registration.models import RegistrationManager, RegistrationProfile
from photologue.models import ImageModel
from ckeditor.fields import RichTextField

from skyhigh import constants, signals, utils
from skyhigh import automatic_emails
from skyhigh.api import sftp_api

from unobase import models as unobase_models

RE_NUMERICAL_SUFFIX = re.compile(r'^[\w-]*-(\d+)+$')

# Entities

class Country(models.Model):
    two_digit_code = models.CharField(max_length=2, unique=True)
    three_digit_code = models.CharField(max_length=3, unique=True)
    dial_code = models.CharField(max_length=6)
    name = models.CharField(max_length=100)
    
    class Meta():
        ordering = ['name']
        verbose_name_plural = 'Countries' 
    
    def __unicode__(self):
        return smart_unicode(self.name)

class StateProvince(models.Model):
    name = models.CharField(max_length=100)
    abbr = models.CharField(max_length=2, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    
    class Meta():
        ordering = ['country', 'name']
        verbose_name_plural = 'States / Provinces' 
        
    def __unicode__(self):
        return smart_unicode(self.name)

class Profile(ImageModel, User):
    title = models.CharField(max_length=8, null=True, blank=True,
                             choices=constants.TITLE_CHOICES)
    phone_number = models.CharField(max_length=16, null=True, blank=True)
    mobile_number = models.CharField(max_length=16, null=True, blank=True)
    address = models.CharField(max_length=512, null=True, blank=True)
    city = models.CharField(max_length=32, null=True, blank=True)
    zip_postal_code = models.CharField(max_length=8, null=True, blank=True)
    state_province = models.ForeignKey(StateProvince, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True)
    company = models.CharField(max_length=128, null=True, blank=True)
    job_title = models.CharField(max_length=32, null=True, blank=True)
    timezone = models.CharField(max_length=64, null=True, blank=True,
                                choices=constants.TIMEZONE_CHOICES)
    role = models.IntegerField(choices=constants.ROLE_CHOICES, 
                               default=constants.ROLE_CHOICE_END_USER)

    maturation_score = models.IntegerField(default=0)
    login_count = models.IntegerField(default=0)
    newsletter_recipient = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    receive_marketing_emails = models.BooleanField(default=True)
    after_login_url = models.URLField(blank=True, null=True)
    industry = models.PositiveSmallIntegerField(choices=constants.INDUSTRY_CHOICES, blank=True, null=True)
    num_employees = models.PositiveSmallIntegerField(choices=constants.NUM_EMPLOYEES_CHOICES, blank=True, null=True)
    requests_or_comments = models.TextField(blank=True, null=True)
    heard_about_from = models.PositiveSmallIntegerField(choices=constants.HEARD_ABOUT_FROM_CHOICES, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    previous_email_addresses = models.CharField(max_length=3000, blank=True, null=True)
    
    search_string = models.CharField(max_length=255, blank=True, null=True)
    search_engine = models.CharField(max_length=255, blank=True, null=True)
    pay_per_click_keyword = models.CharField(max_length=255, blank=True, null=True)

    def update_marketo_score(self, score_type):
        """
        Updates a score record at Marketo
        """
        score = constants.ACTION_POINTS[score_type]
        self.maturation_score += score
        self.save()
    
    @staticmethod
    def generate_username(hint):
        username = hint.replace(' ','').lower()[0:30]
        if User.objects.filter(username=username).count() == 0:
            return username
        
        iteration = 0
        while True:
            iteration += 1
            username = '%s_%d' % (username[0:27], iteration)
            if User.objects.filter(username=username).count() == 0:
                return username
            
    def revalidate_email(self, previous_email):
        self.is_active = False
        self.username = self.email
        if self.previous_email_addresses is not None:
            self.previous_email_addresses += ', %s' % previous_email
        else:
            self.previous_email_addresses = previous_email
        self.save()
        
        try:
            SkyHighRegistrationProfile.objects.get(user=self.user).delete()
        except SkyHighRegistrationProfile.DoesNotExist:
            pass
        
        registration_profile = SkyHighRegistrationProfile.objects.create_profile(self.user)
        
        automatic_emails.email_account_reactivation.delay(registration_profile.id, Site.objects.get_current().id)
    
    def save(self, *args, **kwargs):
        # Generate a username based on either email or full name.
        if not self.username:
            if self.email:
                self.username = Profile.generate_username(self.email)
            else:
                self.username = Profile.generate_username("%s%s" % (self.first_name, self.last_name))
 
        return super(Profile, self).save(*args, **kwargs)
    
    @property
    def display_name(self):
        """Returns the most available name for a user."""
        if self.first_name or self.last_name:
            return self.get_full_name()
        else:
            return self.username
    
    @property
    def user(self):
        return User.objects.get(pk=self.pk)

    @property
    def is_admin(self):
        return self.role >= constants.ROLE_CHOICE_ADMIN or self.user.is_superuser

    @property
    def is_forum_moderator(self):
        return self.role >= constants.ROLE_CHOICE_ADMIN or self.user.is_superuser

    @property
    def is_end_user(self):
        return self.role == constants.ROLE_CHOICE_END_USER


    @property
    def has_incomplete_fields(self):
        if not self.address or not self.city or not self.state_province or not self.country \
            or not self.company or not self.job_title or not self.timezone or not self.industry \
            or not self.num_employees or not self.heard_about_from or not self.website:
                return True
            
        if self.is_partner:
            if not self.partnership.num_branches or not self.partnership.branch_offices \
                or not self.partnership.countries_requesting_to_sell_in \
                or not self.partnership.us_states_requesting_to_sell_in \
                or not self.partnership.annual_revenue or not self.partnership.years_in_business \
                or not self.partnership.num_sales_reps or not self.partnership.num_systems_engineers \
                or not self.partnership.num_technical_support_staff or not self.partnership.business_type \
                or not self.partnership.preferred_distributor or not self.partnership.target_vertical_focus \
                or not self.partnership.resell_to_usa_federal_sectors or not self.partnership.offer_own_support \
                or not self.partnership.manufacturers_selling or not self.partnership.leading_competitors \
                or not self.partnership.representitive or not self.partnership.vat_number or not self.partnership.gst_number \
                or not self.partnership.tax_id_number or not self.partnership.d_and_b_number:
                
                return True
        
        return False

    @property
    def is_cloud_service_provider(self):
        try:
            return self.partnership.cloud_service_provider is not None
        except (AttributeError, Partnership.DoesNotExist, CloudServiceProvider.DoesNotExist):
            return False
        
    @property
    def is_channel_partner(self):
        return self.is_partner and self.partnership.type == constants.PARTNER_TYPE_CHANNEL
        
    @property
    def is_technical_partner(self):
        return self.is_partner and self.partnership.type == constants.PARTNER_TYPE_TECHNOLOGY
        
    @property
    def is_partner(self):
        try:
            return self.partnership is not None and \
                self.partnership.status == constants.PARTNERSHIP_REQUEST_STATUS_APPROVED
        except Partnership.DoesNotExist:
            return False
        
    @property
    def is_product_evaluator(self):
        try:
            return self.evaluation_request is not None and \
                self.evaluation_request.status == constants.PRODUCT_EVALUATION_STATUS_APPROVED
        except (AttributeError, ProductEvaluation.DoesNotExist):
            return False
        
    @property
    def requested_product_evaluation(self):
        try:
            return self.evaluation_request is not None and \
                self.evaluation_request.status == constants.PRODUCT_EVALUATION_STATUS_PENDING
        except (AttributeError, ProductEvaluation.DoesNotExist):
            return False

    @property
    def cloud_service_provider(self):
        try:
            return self.partnership.cloud_service_provider
        except (AttributeError, Partnership.DoesNotExist, CloudServiceProvider.DoesNotExist):
            return None

    @property
    def csp_attributes(self):
        if self.is_cloud_service_provider:
            csp_attribute_list = []
            for csp_attribute in self.cloud_service_provider.attributes.all().order_by('si_number'):
                value = csp_attribute.csp_rel.get(cloud_service_provider__partnership__user=self.user).value

                csp_attribute_list.append({'si_number': csp_attribute.si_number,
                                           'category': csp_attribute.get_category_display(),
                                           'name': csp_attribute.name,
                                           'value': value})

            return csp_attribute_list

        return None



class UserImportHash(models.Model):
    """
    Records hashes of user import CSV files allowing us to track
    duplicate imports and warn users accordingly.
    """
    md5 = models.CharField(max_length=32)
    
class SFTPUser(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, related_name='sftp_user_accounts')
    username = models.CharField(max_length=60, unique=True)
    password = models.CharField(max_length=128)
    
    def __unicode__(self):
        return u'%s' % self.username
    
    def save(self, *args, **kwargs):
        if not self.id:
            sftp_api.create_account(self)
        else:
            if self.password != SFTPUser.objects.get(pk=self.pk).password:
                sftp_api.update_account(self)
            
        return super(SFTPUser, self).save(*args, **kwargs)

class Partnership(models.Model):
    user = models.OneToOneField(User, related_name='partnership')
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(choices=constants.PARTNERSHIP_REQUEST_STATUS_CHOICES, default=constants.PARTNERSHIP_REQUEST_STATUS_PENDING)
    type = models.PositiveSmallIntegerField(choices=constants.PARTNER_TYPE_CHOICES, default=constants.PARTNER_TYPE_TECHNOLOGY)
    modified_by = models.ForeignKey(User, related_name='moderated_partnership', blank=True, null=True)
    modified = models.DateTimeField(auto_now=True)
    
    num_branches = models.PositiveSmallIntegerField(blank=True, null=True)
    branch_offices = models.CharField(max_length=255, blank=True, null=True)
    countries_requesting_to_sell_in = models.CharField(max_length=255, blank=True, null=True)
    us_states_requesting_to_sell_in = models.CharField(max_length=255, blank=True, null=True)
    annual_revenue = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    years_in_business = models.PositiveSmallIntegerField(blank=True, null=True)
    num_sales_reps = models.IntegerField(blank=True, null=True)
    num_systems_engineers = models.IntegerField(blank=True, null=True)
    num_technical_support_staff = models.IntegerField(blank=True, null=True)
    business_type = models.PositiveSmallIntegerField(choices=constants.BUSINESS_TYPE_CHOICES, blank=True, null=True)
    preferred_distributor = models.CharField(max_length=255, blank=True, null=True)
    target_vertical_focus = models.ManyToManyField('TargetVerticalFocus', blank=True, null=True)
    resell_to_usa_federal_sectors = models.PositiveSmallIntegerField(choices=constants.RESELL_TO_USA_FEDERAL_SECTOR_CHOICES, blank=True, null=True)
    offer_own_support = models.PositiveSmallIntegerField(choices=constants.OFFER_OWN_SUPPORT_CHOICES, blank=True, null=True)
    manufacturers_selling = models.CharField(max_length=255, blank=True, null=True)
    leading_competitors = models.CharField(max_length=255, blank=True, null=True)
    additional_comments = models.TextField(blank=True, null=True)
    representitive = models.CharField(max_length=255, blank=True, null=True)
    vat_number = models.CharField(max_length=255, blank=True, null=True)
    gst_number = models.CharField(max_length=255, blank=True, null=True)
    tax_id_number = models.CharField(max_length=255, blank=True, null=True)
    d_and_b_number = models.CharField(max_length=255, blank=True, null=True)
    type_of_technology_selling = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.user.username

    def save(self, *args, **kwargs):
        if self.status == constants.PARTNERSHIP_REQUEST_STATUS_APPROVED:
            user_actions.action_partnership_request_approved(self.user)

            if self.type == constants.PARTNER_TYPE_TECHNOLOGY:
                automatic_emails.email_technical_partner_approved.delay(self.user_id)

            elif self.type == constants.PARTNER_TYPE_CHANNEL:
                automatic_emails.email_channel_partner_approved.delay(self.user_id)

        elif self.status == constants.PARTNERSHIP_REQUEST_STATUS_DECLINED:

            if self.type == constants.PARTNER_TYPE_TECHNOLOGY:
                automatic_emails.email_technical_partner_declined.delay(self.user_id)

            elif self.type == constants.PARTNER_TYPE_CHANNEL:
                automatic_emails.email_channel_partner_declined.delay(self.user_id)

        if self.type == constants.PARTNER_TYPE_TECHNOLOGY:
            self.user.profile.role = constants.ROLE_CHOICE_TECHNICAL_PARTNER
            self.user.profile.save()

        return super(Partnership, self).save(*args, **kwargs)
    
class TargetVerticalFocus(models.Model):
    vertical_focus = models.CharField(max_length=255)
    
    def __unicode__(self):
        return u'%s' % self.vertical_focus

class CSPAttribute(models.Model):
    si_number = models.PositiveSmallIntegerField()
    category = models.PositiveSmallIntegerField(choices=constants.CSP_ATTRIBUTE_CATEGORY_CHOICES)
    name = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u'%s' % self.name
    
class CSPAttributeOption(models.Model):
    name = models.CharField(max_length=250)
    attribute = models.ForeignKey(CSPAttribute, related_name='options')

    def __unicode__(self):
        return u'%s' % self.name

class CloudServiceProvider(models.Model):
    url = models.URLField(blank=True, null=True, max_length=250)
    category = models.PositiveSmallIntegerField(blank=True, null=True, choices=constants.CSP_CATEGORY_CHOICES)
    csp_id = models.IntegerField(blank=True, null=True)
    partnership = models.OneToOneField(Partnership, related_name='cloud_service_provider')
    attributes = models.ManyToManyField(CSPAttribute, through='CSPAttributeThrough')

    def __unicode__(self):
        return u'%s' % self.partnership.user.username

    def save(self, *args, **kwargs):
        profile = self.partnership.user.profile

        if not self.id:
            profile.after_login_url = 'http://%s%s' % (Site.objects.get_current().domain,
                                                                              reverse('my_profile_csp_attributes_update_step', args=('data',)))
        profile.role = constants.ROLE_CHOICE_CLOUD_SERVICE_PROVIDER
        profile.save()

        return super(CloudServiceProvider, self).save(*args, **kwargs)

class CSPAttributeThrough(models.Model):
    cloud_service_provider = models.ForeignKey(CloudServiceProvider)
    cloud_service_provider_attribute = models.ForeignKey(CSPAttribute, related_name='csp_rel')
    value = models.CharField(max_length=3000)

class Reseller(models.Model):
    partnership = models.OneToOneField(Partnership, related_name='reseller')

    def save(self, *args, **kwargs):
        self.partnership.user.profile.role = constants.ROLE_CHOICE_RESELLER
        self.partnership.user.profile.save()

        return super(Reseller, self).save(*args, **kwargs)

class Distributor(models.Model):
    partnership = models.OneToOneField(Partnership, related_name='distributor')

    def save(self, *args, **kwargs):
        self.partnership.user.profile.role = constants.ROLE_CHOICE_DISTRIBUTOR
        self.partnership.user.profile.save()

        return super(Distributor, self).save(*args, **kwargs)
    
class Deal(models.Model):
    partner = models.ForeignKey(Partnership, related_name='deals')
    title = models.CharField(max_length=255)
    content = models.TextField()
    
    def __unicode__(self):
        return u'%s' % self.title

class ProductEvaluation(models.Model):
    user = models.OneToOneField(User, related_name='evaluation_request')
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(choices=constants.PRODUCT_EVALUATION_STATUS_CHOICES,
                                              default=constants.PRODUCT_EVALUATION_STATUS_PENDING)
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='moderated_product_evaluations', blank=True, null=True)
    five_day_email_sent = models.BooleanField(default=False)
    twenty_five_day_email_sent = models.BooleanField(default=False)
    expired_email_sent = models.BooleanField(default=False)
    log_file_sample = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            automatic_emails.email_product_evaluation_initial.delay(self.user_id)

        if self.status == constants.PRODUCT_EVALUATION_STATUS_APPROVED:
            user_actions.action_product_evaluation_request_approved(self.user)
            automatic_emails.email_product_evaluation_started.delay(self.user_id)
            
            SFTPUser.objects.create(user=self.user, 
                                    username=('%s%s' % (self.user.first_name, self.user.last_name)).lower(), 
                                    password=generate(10))
            
        if self.log_file_sample:
            automatic_emails.email_static_page_uploaded.delay(self.user_id, self.log_file_sample)

        self.user.profile.role = constants.ROLE_CHOICE_PRODUCT_OWNER
        self.user.profile.save()

        return super(ProductEvaluation, self).save(*args, **kwargs)

class ContactMessage(models.Model):
    user = models.ForeignKey(User, related_name='contact_messages')
    message = models.TextField()
    sent_date = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(choices=constants.CONTACT_MESSAGE_STATUS_CHOICES,
                                              default=constants.CONTACT_MESSAGE_STATUS_UNREAD)
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='moderated_contact_messages', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            utils.send_mail(None, {}, 'Contact Message from Website', self.message, settings.SKYHIGH_MAILER_EMAIL, [settings.SKYHIGH_INFO_EMAIL])
            automatic_emails.email_information_request.delay(self.user.id)

        if self.status == constants.CONTACT_MESSAGE_STATUS_READ:
            user_actions.action_contact_message_read(self.modified_by)

        elif self.status == constants.CONTACT_MESSAGE_STATUS_RESPONDED:
            user_actions.action_contact_message_responded(self.modified_by)

        return super(ContactMessage, self).save(*args, **kwargs)

class SkyHighRegistrationManager(RegistrationManager):
    
    @classmethod
    def normalize_email(cls, email):
        """
        Normalize the address by lowercasing the domain part of the email
        address.
        """
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name, domain_part.lower()])
        return email
    
    def create_inactive_profile(self, site, request, send_email=True, **kwargs):

        now = timezone.now()
        email = SkyHighRegistrationManager.normalize_email(kwargs['email'])
        profile = Profile.objects.create(username=email, first_name=kwargs['first_name'], last_name=kwargs['last_name'],
                                         email=kwargs['email'], is_staff=False, is_active=False, 
                                         is_superuser=False, last_login=now, date_joined=now)
        
        if kwargs.has_key('search_string'):
            profile.search_string = kwargs['search_string']
            
        if kwargs.has_key('search_engine'):
            profile.search_engine = kwargs['search_engine']
            
        if kwargs.has_key('pay_per_click_keyword'):
            profile.pay_per_click_keyword = kwargs['pay_per_click_keyword']
        
        if kwargs.has_key('company'):
            profile.company = kwargs['company']
        
        if kwargs.has_key('job_title'):
            profile.job_title = kwargs['job_title']
        
        if kwargs.has_key('phone_number'):
            profile.phone_number = kwargs['phone_number']

        if kwargs.has_key('newsletter_recipient'):
            profile.newsletter_recipient = kwargs['newsletter_recipient']
            
        if kwargs.has_key('zip_postal_code'):
            profile.zip_postal_code = kwargs['zip_postal_code']
            
        if kwargs.has_key('requests_or_comments'):
            profile.requests_or_comments = kwargs['requests_or_comments']

        if kwargs.has_key('password1'):
            profile.set_password(kwargs['password1'])
        else:
            profile.set_unusable_password()

        # First save everything before we send signals or emails.
        profile.save(using=self._db)

        if kwargs.has_key('request_evaluation'):
            if kwargs['request_evaluation']:
                product_evaluation = ProductEvaluation.objects.create(user=profile.user,
                    status=constants.PARTNERSHIP_REQUEST_STATUS_PENDING)

                signals.user_requested_evaluation.send(sender=self.__class__,
                                                       user=profile.user,
                                                       request=request)

                user_actions.action_product_evaluation_request(profile.user, True)

        if kwargs.has_key('request_partnership'):
            if kwargs['request_partnership']:
                partnership = Partnership.objects.create(user=profile.user,
                    status=constants.PARTNERSHIP_REQUEST_STATUS_PENDING)

                signals.user_requested_partnership.send(sender=self.__class__,
                                                        user=profile.user,
                                                        request=request)

        registration_profile = self.create_profile(profile.user)
        
        if send_email:
            automatic_emails.email_account_activation.delay(registration_profile.id, site.id)

        return profile
    
    create_inactive_profile = transaction.commit_on_success(create_inactive_profile)
    
class SkyHighRegistrationProfile(RegistrationProfile):

    objects = SkyHighRegistrationManager()
    
    def send_activation_email(self, site):

        ctx_dict = {'user' : self.user,
                    'activation_key': self.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site,
                    'app_name': settings.APP_NAME}
        
        # Email subject *must not* contain newlines
        subject = ''.join(render_to_string('registration/activation_email_subject.txt',
                                   ctx_dict).splitlines())
        
        text_content = render_to_string('registration/activation_email.txt',
                                        ctx_dict)
        
        utils.send_mail('registration/activation_email.html', ctx_dict, subject,
                        text_content, settings.DEFAULT_FROM_EMAIL, [self.user.email,], None)
        
    def send_reactivation_email(self, site):

        ctx_dict = {'user' : self.user,
                    'activation_key': self.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site,
                    'app_name': settings.APP_NAME}
        
        # Email subject *must not* contain newlines
        subject = ''.join(render_to_string('registration/reactivation_email_subject.txt',
                                   ctx_dict).splitlines())
        
        text_content = render_to_string('registration/reactivation_email.txt',
                                        ctx_dict)
        
        utils.send_mail('registration/reactivation_email.html', ctx_dict, subject,
                        text_content, settings.DEFAULT_FROM_EMAIL, [self.user.email,], None)
        
class UserActivity(models.Model):
    user = models.ForeignKey(User)
    action = models.CharField(max_length=40, choices=constants.ACTION_CHOICES)
    object_content_type = models.ForeignKey(ContentType, null=True, blank=True,
                                            related_name='user_activity_object')
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object = generic.GenericForeignKey('object_content_type', 'object_id')
    content_object_content_type = models.ForeignKey(ContentType, null=True, blank=True, 
                                                    related_name='user_activity_content_object')
    content_object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_object_content_type', 'content_object_id')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta():
        ordering = ['-timestamp']
        verbose_name_plural = 'User activities' 
        
    @staticmethod
    def track(user, action, the_object=None, content_object=None):
        if the_object and content_object:
            return UserActivity.objects.create(user=user,
                                               action=action,
                                               object_content_type=ContentType.objects.get_for_model(the_object),
                                               object_id=the_object.id,
                                               content_object_content_type=ContentType.objects.get_for_model(content_object),
                                               content_object_id=content_object.id
                                               )
        else:
            return UserActivity.objects.create(user=user, action=action)


# Content Objects


class PressRelease(unobase_models.ContentModel):
    
    objects = models.Manager()
    permitted = unobase_models.StateManager()
    
    default_image_category = constants.DEFAULT_IMAGE_CATEGORY_PRESS_RELEASE
    
    pdf = models.FileField(upload_to='press_releases', blank=True, null=True)

class MediaCoverage(unobase_models.ContentModel):
    
    objects = models.Manager()
    permitted = unobase_models.StateManager()
    
    default_image_category = constants.DEFAULT_IMAGE_CATEGORY_MEDIA_COVERAGE

    pdf = models.FileField(upload_to='media_coverages', blank=True, null=True)
    external_link = models.URLField(blank=True, null=True)
    image_name = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
class Resource(unobase_models.ContentModel):
    
    objects = models.Manager()
    permitted = unobase_models.StateManager()
    
    default_image_category = constants.DEFAULT_IMAGE_CATEGORY_RESOURCE

    pdf = models.FileField(upload_to='resources', blank=True, null=True)
    external_link = models.URLField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    image_name = models.CharField(max_length=100, blank=True, null=True, unique=True)
    type = models.CharField(max_length=255, choices=constants.RESOURCE_TYPES)
    
    @property
    def resource_url(self):
#         if self.type in ['whitepapers', 'datasheets']:
#             return self.pdf.url
        
        return self.external_link
    
class ConfigurableEmail(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=255, default='')
    content = RichTextField(blank=True, null=True)
    plaintext_content = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=255, editable=False, db_index=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    variables = models.ManyToManyField('ConfigurableEmailVariable', blank=True, null=True)
    internal_bccs = models.ManyToManyField('ConfigurableEmailInternalBCC', blank=True, null=True)
    send_reason = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return u'%s' % self.title
    
    @property
    def internal_bcc_list_string(self):
        internal_bccs = self.internal_bccs.all()
        
        if not internal_bccs:
            return None
        
        return ', '.join([internal_bcc.email for internal_bcc in internal_bccs])
    
    @property
    def internal_bcc_list(self):
        internal_bccs = self.internal_bccs.all()
        
        return [internal_bcc.email for internal_bcc in internal_bccs]

    def generate_slug(self, obj, text, tail_number=0):
        """
        Returns a new unique slug. Object must provide a SlugField called slug.
        URL friendly slugs are generated using django.template.defaultfilters'
        slugify. Numbers are added to the end of slugs for uniqueness.
        """
        # use django slugify filter to slugify
        slug = slugify(text)
    
        # Empty slugs are ugly (eg. '-1' may be generated) so force non-empty
        if not slug:
            slug = 'no-title'
            
        query = ConfigurableEmail.objects.filter(
            slug__startswith=slug
        ).exclude(id=obj.id).order_by('-id')
    
        # No collisions
        if not query.count():
            return slug
    
        # Match numerical suffix if it exists
        match = RE_NUMERICAL_SUFFIX.match(query[0].slug)
        if match is not None:
            return "%s-%s" % (slug, int(match.group(1)) + 1)
        else:
            return "%s-1" % slug

    def save(self, *args, **kwargs):
        if not self.created:
            self.created = timezone.now()
            self.slug = self.generate_slug(self, self.title)

        return super(ConfigurableEmail, self).save(*args, **kwargs)
    
class ConfigurableEmailVariable(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return u'%s' % self.name
    
class ConfigurableEmailInternalBCC(models.Model):
    email = models.EmailField(unique=True)
    
    def __unicode__(self):
        return u'%s' % self.email

class Event(unobase_models.ContentModel):
    
    objects = models.Manager()
    permitted = unobase_models.StateManager()
    
    default_image_category = constants.DEFAULT_IMAGE_CATEGORY_EVENT
    
    start_date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    external_link = models.URLField(blank=True, null=True)
    image_name = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
    def save(self, *args, **kwargs):
        return super(Event, self).save(*args, **kwargs)
    
class Leader(unobase_models.ContentModel):
    
    objects = models.Manager()
    permitted = unobase_models.StateManager()
    
    job_title = models.CharField(max_length=100, blank=True, null=True)
    
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return u'%s' % self.title
    
class Investor(unobase_models.ContentModel):
    
    objects = models.Manager()
    permitted = unobase_models.StateManager()
    
    def __unicode__(self):
        return u'%s' % self.title
    
class CaseStudy(unobase_models.ContentModel):
    
    objects = models.Manager()
    permitted = unobase_models.StateManager()
    
    has_detail = models.BooleanField(default=True)
    pdf = models.FileField(upload_to='case_studies', blank=True, null=True)
    
    quote = models.TextField(blank=True, null=True)
    quote_by = models.CharField(max_length=255, blank=True, null=True)
    
    def __unicode__(self):
        return u'%s' % self.title

class Career(unobase_models.ContentModel):
    
    objects = models.Manager()
    permitted = unobase_models.StateManager()
    
    
    
    position = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%s' % self.position

class CareerApplication(models.Model):
    career = models.ForeignKey(Career)
    user = models.OneToOneField(User, blank=True, null=True, related_name='career_application')
    cv_file = models.FileField(upload_to='careers/cv_uploads', blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'%s - %s' % (self.user, self.career)
    
class SplashScreenContact(models.Model):
    """
    Stores email addresses from the splash screen.
    """
    email = models.EmailField()

###############################################################################
# Signals

def check_profile(sender, instance, created, **kwargs):
    if created:
        try:
            Profile.objects.get(pk=instance.pk)
        except:
            kwargs = {'user_ptr_id' : instance.pk}
            Profile.objects.create(**kwargs)

models.signals.post_save.connect(check_profile, sender=User)

from unobase.commenting import signals as commenting_signals
from unobase.support import signals as support_signals
import user_actions

def user_commented_handler(sender, user, request, comment, **kwargs):
    content_type = ContentType.objects.get(pk=comment.content_type_id)
    object = content_type.get_object_for_this_type(pk=comment.object_pk)

    if content_type.model == 'blogentry':
        user_actions.action_blog_entry_comment(user, object)

commenting_signals.user_commented.connect(user_commented_handler)

def user_submitted_support_case_handler(sender, user, request, case, **kwargs):
    user_actions.action_support_case_submitted(case)

support_signals.user_submitted_support_case.connect(user_submitted_support_case_handler)

def user_requested_evaluation_handler(sender, user, request, **kwargs):
    pass

signals.user_requested_evaluation.connect(user_requested_evaluation_handler)

def user_requested_partnership_handler(sender, user, request, **kwargs):
    pass

signals.user_requested_partnership.connect(user_requested_partnership_handler)

###############################################################################
# Patches

# Make the username field longer so an email address could be used
#https://github.com/GoodCloud/django-longer-username/blob/master/longerusername/models.py
    
MAX_USERNAME_LENGTH = 75
    
def longer_username_signal(sender, *args, **kwargs):
    if (sender.__name__ == "User" and
        sender.__module__ == "django.contrib.auth.models"):
        patch_user_model(sender)
models.signals.class_prepared.connect(longer_username_signal)

def patch_user_model(model):
    field = model._meta.get_field("username")

    field.max_length = MAX_USERNAME_LENGTH

    # patch model field validator because validator doesn't change if we change
    # max_length
    for v in field.validators:
        if isinstance(v, MaxLengthValidator):
            v.limit_value = MAX_USERNAME_LENGTH

# https://github.com/GoodCloud/django-longer-username/issues/1
# django 1.3.X loads User model before class_prepared signal is connected
# so we patch model after it's prepared

# check if User model is patched
if User._meta.get_field("username").max_length != MAX_USERNAME_LENGTH:
    patch_user_model(User)
    
###############################################################################
