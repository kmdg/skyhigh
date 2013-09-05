__author__ = 'michael'

from celery.decorators import task

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils import timezone
from django.utils.http import int_to_base36
from django.contrib.auth.tokens import default_token_generator
from django.core.files.base import ContentFile

from skyhigh import utils, constants

@task(default_retry_delay=10 * 60)
def email_account_activation(registration_profile_id, site_id):
    try:
        from skyhigh import models
        registration_profile = models.SkyHighRegistrationProfile.objects.get(pk=registration_profile_id)
        site = Site.objects.get(pk=site_id)
        
        ctx_dict = {'user' : registration_profile.user,
                    'activation_key': registration_profile.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site,
                    'app_name': settings.APP_NAME,
                    'display_name': registration_profile.user.profile.display_name,
                    'username': registration_profile.user.username}
        
        # Email subject *must not* contain newlines
        configurable_email = models.ConfigurableEmail.objects.get(slug='account-activation')
        
        subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
        
        text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
        
        html_content = utils.get_configurable_email_html_content(configurable_email, ctx_dict)
        
        utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                        [registration_profile.user.email] + configurable_email.internal_bcc_list, html_content=html_content)
    except Exception, exc:
        raise email_account_activation.retry(exc=exc)
    
@task(default_retry_delay=10 * 60)
def email_account_reactivation(registration_profile_id, site_id):
    try:
        from skyhigh import models
        registration_profile = models.SkyHighRegistrationProfile.objects.get(pk=registration_profile_id)
        site = Site.objects.get(pk=site_id)
        
        ctx_dict = {'user' : registration_profile.user,
                    'activation_key': registration_profile.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site,
                    'app_name': settings.APP_NAME,
                    'display_name': registration_profile.user.profile.display_name,
                    'username': registration_profile.user.username}
        
        # Email subject *must not* contain newlines
        configurable_email = models.ConfigurableEmail.objects.get(slug='account-reactivation')
        
        subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
        
        text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
        
        html_content = utils.get_configurable_email_html_content(configurable_email, ctx_dict)
        
        utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                        [registration_profile.user.email] + configurable_email.internal_bcc_list, html_content=html_content)
    except Exception, exc:
        raise email_account_reactivation.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def email_successful_account_activation(user_id):
    try:
        from skyhigh import models
        
        user = User.objects.get(pk=user_id)
    
        ctx_dict = utils.get_email_context(user)
    
        ctx_dict.update({'uid': int_to_base36(user.id),
                         'token': default_token_generator.make_token(user),
                         'display_name': user.profile.display_name,
                         'username': user.username})
        
        configurable_email = models.ConfigurableEmail.objects.get(slug='successful-account-activation')
    
        subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
        
        text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
        
        html_content = utils.get_configurable_email_html_content(configurable_email, ctx_dict)
    
        utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                        [user.email] + configurable_email.internal_bcc_list, user=user, html_content=html_content)
    except Exception, exc:
        raise email_successful_account_activation.retry(exc=exc)
    
@task(default_retry_delay=10 * 60)
def email_existing_csp_activation(user_id):
    try:
        from skyhigh import models
        
        user = User.objects.get(pk=user_id)
    
        ctx_dict = utils.get_email_context(user)
    
        ctx_dict.update({'uid': int_to_base36(user.id),
                         'token': default_token_generator.make_token(user),
                         'display_name': user.profile.display_name,
                         'username': user.username})
        
        configurable_email = models.ConfigurableEmail.objects.get(slug='existing-csp-activation')
    
        subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
        
        text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
        
        html_content = utils.get_configurable_email_html_content(configurable_email, ctx_dict)
    
        utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                        [user.email] + configurable_email.internal_bcc_list, user=user, html_content=html_content)
    except Exception, exc:
        raise email_existing_csp_activation.retry(exc=exc)
    
@task(default_retry_delay=10 * 60)
def email_password_reset_new_token(user_id):
    try:
        user = User.objects.get(pk=user_id)
    
        ctx_dict = utils.get_email_context(user)
    
        ctx_dict.update({'uid': int_to_base36(user.id),
                         'token': default_token_generator.make_token(user),
                        })
        
        print ctx_dict
    
        subject = utils.get_email_subject('registration/password_reset_email_subject.txt', ctx_dict)
    
        text_content = utils.get_email_text_content('registration/password_reset_email.txt', ctx_dict)
    
        utils.send_mail('registration/password_reset_email.html', ctx_dict, subject,
            text_content, settings.DEFAULT_FROM_EMAIL, [user.email,], user=user)
    except Exception, exc:
        raise email_password_reset_new_token.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def email_channel_partner_request(user_id):
    try:
        from skyhigh import models
        
        user = User.objects.get(pk=user_id)
        
        if user.profile.email_notifications:
            ctx_dict = utils.get_email_context(user)
            
            ctx_dict.update({'display_name': user.profile.display_name,})
            
            configurable_email = models.ConfigurableEmail.objects.get(slug='channel-partner-request')
        
            subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
        
            text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
            
            html_content = utils.get_configurable_email_html_content(configurable_email, ctx_dict)
        
            utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                            [user.email] + configurable_email.internal_bcc_list, user=user, html_content=html_content)
    except Exception, exc:
        raise email_channel_partner_request.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def email_technical_partner_request(user_id):
    try:
        from skyhigh import models
        
        user = User.objects.get(pk=user_id)
    
        if user.profile.email_notifications:
            ctx_dict = utils.get_email_context(user)
            
            ctx_dict.update({'display_name': user.profile.display_name,})
            
            configurable_email = models.ConfigurableEmail.objects.get(slug='technical-partner-request')
        
            subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
        
            text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
            
            html_content = utils.get_configurable_email_html_content(configurable_email, ctx_dict)
        
            utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                            [user.email] + configurable_email.internal_bcc_list, user=user, html_content=html_content)
    except Exception, exc:
        raise email_technical_partner_request.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def email_channel_partner_approved(user_id):
    try:
        from skyhigh import models
        
        user = User.objects.get(pk=user_id)
    
        if user.profile.email_notifications:
            ctx_dict = utils.get_email_context(user)
            
            ctx_dict.update({'display_name': user.profile.display_name,})
            
            configurable_email = models.ConfigurableEmail.objects.get(slug='channel-partner-request-approved')
        
            subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
        
            text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
            
            html_content = utils.get_configurable_email_html_content(configurable_email, ctx_dict)
        
            utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                            [user.email] + configurable_email.internal_bcc_list, user=user, html_content=html_content)
    except Exception, exc:
        raise email_channel_partner_approved.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def email_channel_partner_declined(user_id):
    try:
        from skyhigh import models
        
        user = User.objects.get(pk=user_id)
    
        if user.profile.email_notifications:
            ctx_dict = utils.get_email_context(user)
            
            ctx_dict.update({'display_name': user.profile.display_name,})
            
            configurable_email = models.ConfigurableEmail.objects.get(slug='channel-partner-request-declined')
        
            subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
        
            text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
            
            html_content = utils.get_configurable_email_html_content(configurable_email, ctx_dict)
        
            utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                            [user.email] + configurable_email.internal_bcc_list, user=user, html_content=html_content)
    except Exception, exc:
        raise email_channel_partner_declined.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def email_technical_partner_approved(user_id):
    try:
        from skyhigh import models
        
        user = User.objects.get(pk=user_id)
    
        if user.profile.email_notifications:
            ctx_dict = utils.get_email_context(user)
            
            ctx_dict.update({'display_name': user.profile.display_name,})
            
            configurable_email = models.ConfigurableEmail.objects.get(slug='technical-partner-request-approved')
        
            subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
        
            text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
            
            html_content = utils.get_configurable_email_html_content(configurable_email, ctx_dict)
        
            utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                            [user.email] + configurable_email.internal_bcc_list, user=user, html_content=html_content)
    except Exception, exc:
        raise email_technical_partner_approved.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def email_technical_partner_declined(user_id):
    try:
        from skyhigh import models
        
        user = User.objects.get(pk=user_id)
    
        if user.profile.email_notifications:
            ctx_dict = utils.get_email_context(user)
            
            ctx_dict.update({'display_name': user.profile.display_name,})
            
            configurable_email = models.ConfigurableEmail.objects.get(slug='technical-partner-request-declined')
        
            subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
        
            text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
            
            html_content = utils.get_configurable_email_html_content(configurable_email, ctx_dict)
        
            utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                            [user.email] + configurable_email.internal_bcc_list, user=user, html_content=html_content)
    except Exception, exc:
        raise email_technical_partner_declined.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def email_information_request(user_id):
    try:
        user = User.objects.get(pk=user_id)
    
        ctx_dict = utils.get_email_context(user)
    
        subject = utils.get_email_subject('skyhigh/email/subjects/information_request_subject.txt', ctx_dict)
    
        text_content = utils.get_email_text_content('skyhigh/email/txt/information_request.txt', ctx_dict)
    
        utils.send_mail('skyhigh/email/html/information_request.html', ctx_dict, subject,
            text_content, settings.DEFAULT_FROM_EMAIL, [user.email,], user=user)
    except Exception, exc:
        raise email_information_request.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def email_support_request(user_id):
    try:
        user = User.objects.get(pk=user_id)
    
        ctx_dict = utils.get_email_context(user)
    
        subject = utils.get_email_subject('skyhigh/email/subjects/support_request_subject.txt', ctx_dict)
    
        text_content = utils.get_email_text_content('skyhigh/email/txt/support_request.txt', ctx_dict)
    
        utils.send_mail('skyhigh/email/html/support_request.html', ctx_dict, subject,
            text_content, settings.DEFAULT_FROM_EMAIL, [user.email,], user=user)
    except Exception, exc:
        raise email_support_request.retry(exc=exc)

@task()
def email_product_evaluation_started(user_id):
    user = User.objects.get(pk=user_id)

    ctx_dict = utils.get_email_context(user)

    subject = utils.get_email_subject('skyhigh/email/subjects/product_evaluation_started_subject.txt', ctx_dict)

    text_content = utils.get_email_text_content('skyhigh/email/txt/product_evaluation_started.txt', ctx_dict)

#    utils.send_mail('skyhigh/email/html/product_evaluation_started.html', ctx_dict, subject,
#        text_content, settings.DEFAULT_FROM_EMAIL, [user.email,], user=user)

@task()
def email_product_evaluation_5_days_in():
    from skyhigh import models

    for product_evaluation in models.ProductEvaluation.objects.filter(status=constants.PRODUCT_EVALUATION_STATUS_APPROVED,
                                                                        modified__lte=timezone.now()-timezone.timedelta(days=5),
                                                                        five_day_email_sent=False):

        user = product_evaluation.user

        ctx_dict = utils.get_email_context(user)

        subject = utils.get_email_subject('skyhigh/email/subjects/product_evaluation_5_days_in_subject.txt', ctx_dict)

        text_content = utils.get_email_text_content('skyhigh/email/txt/product_evaluation_5_days_in.txt', ctx_dict)

#        utils.send_mail('skyhigh/email/html/product_evaluation_5_days_in.html', ctx_dict, subject,
#            text_content, settings.DEFAULT_FROM_EMAIL, [user.email,], user=user)
#
#        product_evaluation.five_day_email_sent = True
#        product_evaluation.save()

@task()
def email_product_evaluation_25_days_in():
    from skyhigh import models

    for product_evaluation in models.ProductEvaluation.objects.filter(status=constants.PRODUCT_EVALUATION_STATUS_APPROVED,
                                                                        modified__lte=timezone.now()-timezone.timedelta(days=25),
                                                                        twenty_five_day_email_sent=False):

        user = product_evaluation.user

        ctx_dict = utils.get_email_context(user)

        subject = utils.get_email_subject('skyhigh/email/subjects/product_evaluation_25_days_in_subject.txt', ctx_dict)

        text_content = utils.get_email_text_content('skyhigh/email/txt/product_evaluation_25_days_in.txt', ctx_dict)

#        utils.send_mail('skyhigh/email/html/product_evaluation_25_days_in.html', ctx_dict, subject,
#            text_content, settings.DEFAULT_FROM_EMAIL, [user.email,], user=user)
#
#        product_evaluation.twenty_five_day_email_sent = True
#        product_evaluation.save()

@task()
def email_product_evaluation_expired():
    from skyhigh import models

    for product_evaluation in models.ProductEvaluation.objects.filter(status=constants.PRODUCT_EVALUATION_STATUS_APPROVED,
                                                                        modified__lte=timezone.now()-timezone.timedelta(days=30),
                                                                        expired_email_sent=False):

        user = product_evaluation.user

        ctx_dict = utils.get_email_context(user)

        subject = utils.get_email_subject('skyhigh/email/subjects/product_evaluation_expired_subject.txt', ctx_dict)

        text_content = utils.get_email_text_content('skyhigh/email/txt/product_evaluation_expired.txt', ctx_dict)

#        utils.send_mail('skyhigh/email/html/product_evaluation_expired.html', ctx_dict, subject,
#            text_content, settings.DEFAULT_FROM_EMAIL, [user.email,], user=user)
#
#        product_evaluation.expired_email_sent = True
#        product_evaluation.save()

@task()
def email_order_processed_end_user(user_id):
    user = User.objects.get(pk=user_id)

    ctx_dict = utils.get_email_context(user)

    subject = utils.get_email_subject('skyhigh/email/subjects/order_processed_end_user_subject.txt', ctx_dict)

    text_content = utils.get_email_text_content('skyhigh/email/txt/order_processed_end_user.txt', ctx_dict)

    utils.send_mail('skyhigh/email/html/order_processed_end_user.html', ctx_dict, subject,
        text_content, settings.DEFAULT_FROM_EMAIL, [user.email,], user=user)

@task()
def email_order_processed_channel_partner(user_id):
    user = User.objects.get(pk=user_id)

    ctx_dict = utils.get_email_context(user)

    subject = utils.get_email_subject('skyhigh/email/subjects/order_processed_channel_partner_subject.txt', ctx_dict)

    text_content = utils.get_email_text_content('skyhigh/email/txt/order_processed_channel_partner.txt', ctx_dict)

    utils.send_mail('skyhigh/email/html/order_processed_channel_partner.html', ctx_dict, subject,
        text_content, settings.DEFAULT_FROM_EMAIL, [user.email,], user=user)

# Admin stuff

@task(default_retry_delay=10 * 60)
def email_sftp_account_created(username, password):
    try:
        from skyhigh import models
        
        user = User.objects.get(pk=1)
        
        ctx_dict = {'username': username,
                    'password': password}
        
        configurable_email = models.ConfigurableEmail.objects.get(slug='internal-sftp-account-created')
    
        subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
    
        text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
    
        utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                        ['stefanka@skyhighnetworks.com', 'dev@unomena.com'] + configurable_email.internal_bcc_list, user=user)
    except Exception, exc:
        raise email_sftp_account_created.retry(exc=exc)
    
@task(default_retry_delay=10 * 60)
def email_sftp_file_uploaded(file_path):
    try:
        from skyhigh import models
        
        user = User.objects.get(pk=1)
        
        ctx_dict = {'file_path': file_path,
                    'username': file_path.split('/')[3]}
        
        configurable_email = models.ConfigurableEmail.objects.get(slug='internal-sftp-file-uploaded')
    
        subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
    
        text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
    
        utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                        ['adam@skyhighnetworks.com', 'dev@unomena.com'] + configurable_email.internal_bcc_list, user=user)
    except Exception, exc:
        raise email_sftp_file_uploaded.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def email_product_evaluation_initial(user_id):
    try:
        from skyhigh import models
        
        user = User.objects.get(pk=user_id)
    
        ctx_dict = utils.get_email_context(user)
        
        ctx_dict.update({'display_name': user.profile.display_name,
                         'user_email': user.email,
                         'company': user.profile.company,
                         'country': user.profile.country,
                         'state_province': user.profile.state_province})
        
        configurable_email = models.ConfigurableEmail.objects.get(slug='internal-product-evaluation-request')
    
        subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
    
        text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
    
        utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                        [settings.SKYHIGH_SALES_EMAIL] + configurable_email.internal_bcc_list, user=user)
    except Exception, exc:
        raise email_product_evaluation_initial.retry(exc=exc)

@task(default_retry_delay=10 * 60)
def email_csp_attributes_updated(user_id):
    try:
        from skyhigh import models
        
        user = User.objects.get(pk=user_id)
    
        ctx_dict = utils.get_email_context(user)
        
        ctx_dict.update({'display_name': user.profile.display_name,
                         'user_email': user.email,
                         'user_id': user.pk,
                         'site': Site.objects.get_current(),
                         'csp_attributes': user.profile.csp_attributes})
        
        configurable_email = models.ConfigurableEmail.objects.get(slug='internal-csp-attributes-updated')
    
        subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
    
        text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
    
        utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                        [settings.SKYHIGH_INFO_EMAIL] + configurable_email.internal_bcc_list, user=user)
    except Exception, exc:
        raise email_csp_attributes_updated.retry(exc=exc)
    
    
@task(default_retry_delay=10 * 60)
def email_static_page_uploaded(user_id, log_file_sample):
    try:
        from skyhigh import models
        
        user = User.objects.get(pk=user_id)
    
        ctx_dict = utils.get_email_context(user)
        
        ctx_dict.update({'display_name': user.profile.display_name,
                         'user_email': user.email})
        
        output = ContentFile(log_file_sample, 'log_file_sample.txt')
    
        configurable_email = models.ConfigurableEmail.objects.get(slug='internal-log-file-sample-uploaded')
    
        subject = utils.get_configurable_email_subject(configurable_email, ctx_dict)
    
        text_content = utils.get_configurable_email_text_content(configurable_email, ctx_dict)
    
        utils.send_mail(None, ctx_dict, subject, text_content, settings.DEFAULT_FROM_EMAIL, 
                        [settings.SKYHIGH_INFO_EMAIL] + configurable_email.internal_bcc_list, attachments=[output], user=user)
    except Exception, exc:
        raise email_static_page_uploaded.retry(exc=exc)
