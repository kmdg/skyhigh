'''
Created on 29 Dec 2012

@author: euan
'''
from django.conf.urls.defaults import patterns, include, url
from django.views import generic as generic_views
from django.views.generic import simple as simple_views
from django.contrib.auth.decorators import login_required

from registration.views import register, activate
from skyhigh import forms, models, views

NAMED_CSP_UPDATE_FORMS = (
    ('data', forms.MyProfileCSPAttributesDataForm),
    ('user_device', forms.MyProfileCSPAttributesUserDeviceForm),
    ('service', forms.MyProfileCSPAttributesServiceForm),
    ('business_risk', forms.MyProfileCSPAttributesBusinessRiskForm),
    ('legal', forms.MyProfileCSPAttributesLegalForm),
    )

urlpatterns = patterns('',

    (r'^skyhigh/api/', include('skyhigh.api.urls')),
    (r'^console/', include('skyhigh.console.urls')),

    url(r'^$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/index.html'}, 
        name='index'),
                       
    url(r'^marketing/emails/unsubscribe/$',
        views.MarketingEmailsUnsubscribeExternal.as_view(template_name='skyhigh/marketing_email_unsubscribe.html'),
        name='marketing_email_unsubscribe_external'),
                       
    url(r'^marketing/emails/unsubscribe/(?P<user_id>\d+)-(?P<token>.+)/$',
        views.MarketingEmailsUnsubscribe.as_view(template_name='skyhigh/marketing_email_unsubscribe.html'),
        name='marketing_email_unsubscribe'),
    
    url(r'^splash/$',
        generic_views.CreateView.as_view(model=models.SplashScreenContact,
                                         template_name='skyhigh/splash.html',
                                         success_url='/splash/thanks/'), 
        name='splash'),

    url(r'^splash/thanks/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/splash_thanks.html'}, 
        name='splash_thanks'),
                       
    url(r'^accounts/activation_complete/(?P<evaluation_requested>\w+)/$',
        views.PostActivation.as_view(template_name='registration/activation_complete.html'),
        name='post_activate'),

    url(r'^secure/accounts/activate/(?P<activation_key>\w+)/$', views.activate,
        {'backend': 'skyhigh.backends.SkyHighRegistrationBackend',
         'success_url': '/accounts/activation_complete/%(evaluation_requested)s'},
        name='secure_activate'),
                       
    url(r'^secure/accounts/register/$', register,
        {'backend': 'skyhigh.backends.SkyHighRegistrationBackend'},
        name='secure_register'),
                       
    url(r'^secure/accounts/password_reset/$',
        'django.contrib.auth.views.password_reset', 
        {'password_reset_form' : forms.SkyHighPasswordResetForm },
        name='secure_password_reset'),

    url(r'^secure/accounts/reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'skyhigh.views.password_reset_confirm',
        name='secure_password_reset_confirm'),
                       
    url(r'^secure/accounts/login/$',
        views.login,
        {'template_name' : 'registration/login.html' },
        name='secure_login'),
                       
    url(r'^accounts/logout/$', 
        views.logout,
        {'template_name' : 'registration/logged_out.html' },
        name='auth_logout'),
                       
    url(r'^secure/complete_my_profile/$',
        views.MyProfile.as_view(form_class=forms.CompleteMyProfileForm,
                                template_name='skyhigh/complete_my_profile.html'), 
        name='complete_my_profile'),

    url(r'^secure/my_profile/$',
        views.MyProfile.as_view(form_class=forms.MyProfileForm,
                                template_name='skyhigh/my_profile.html'), 
        name='my_profile'),
                       
    url(r'^secure/my_profile/sftp_account_list/$',
        views.SFTPAccountList.as_view(template_name='skyhigh/my_profile_sftp_account_list.html'), 
        name='my_profile_sftp_account_list'),
                       
    url(r'^secure/my_profile/sftp_account/(?P<pk>\d+)/$',
        views.SFTPAccountUpdate.as_view(form_class=forms.SFTPAccount,
                                template_name='skyhigh/my_profile_sftp_account.html'), 
        name='my_profile_sftp_account'),
                       
    url(r'^secure/my_profile/log_file_sample/upload/$',
        views.LogFileSampleUpload.as_view(form_class=forms.LogFileSampleForm,
                                template_name='skyhigh/my_profile_log_file_sample.html'), 
        name='my_profile_log_file_sample_upload'),

    url(r'^secure/my_profile/csp_attributes/update/(?P<step>.+)/$',
        views.MyProfileCSPAttributesUpdate.as_view(NAMED_CSP_UPDATE_FORMS,
            url_name='my_profile_csp_attributes_update_step', done_step_name='complete'),
        name='my_profile_csp_attributes_update_step'),
                       
    url(r'^password_reset_new_token/(?P<user_id>\d+)/$',
        views.PasswordResetNewToken.as_view(template_name='registration/password_reset_new_token.html'), 
        name='password_reset_new_token'),

    # Main Sellers

    url(r'^rethink-cloud/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/rethink_cloud.html'}, 
        name='rethink_cloud'),

    url(r'^cloud-security-product-tour/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/product_tour.html'}, 
        name='product_tour'),
                       
    # Product

    url(r'^product/overview/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/product/product_overview.html'}, 
        name='product_overview'),
                       
    #/product subpages 
    url(r'^product/overview-shadow-it/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/product/product_overview_shadow_it.html'}, 
        name='product_overview_shadow_it'),
     
    url(r'^product/overview-saas-security/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/product/product_overview_saas_security.html'}, 
        name='product_overview_saas_security'),
     
    url(r'^product/overview-cloud-control/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/product/product_overview_cloud_control.html'}, 
        name='product_overview_cloud_control'),   

    url(r'^product/architecture/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/product/product_architecture.html'}, 
        name='product_architecture'),

    url(r'^product/evaluation/$',
        views.RequestEvaluation.as_view(form_class=forms.RequestEvaluationForm,
                                        template_name='skyhigh/product/evaluation/product_evaluation_request_form.html'),
        name='product_evaluation'),

    url(r'^product/evaluation/thanks/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/product/evaluation/product_evaluation_request_thanks.html'}, 
        name='product_evaluation_thanks'),

    url(r'^secure/product/evaluation/complete/signup/$',
        views.CompleteEvaluationSignup.as_view(form_class=forms.CompleteUserProfileForm,
            template_name='skyhigh/product/evaluation/complete_evaluation_signup.html',
            success_url='/product/evaluation/thanks/'),
        name='complete_evaluation_signup'),

    url(r'^product/evaluation/already_submitted/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/product/evaluation/product_evaluation_request_already_submitted.html'}, 
        name='product_evaluation_already_submitted'),

    url(r'^product/use_cases/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/product/product_use_cases.html'}, 
        name='product_use_cases'),
                       
    url(r'^product/case_studies/$',
        views.CaseStudyList.as_view(template_name='skyhigh/product/case_studies/case_study_list.html',
                                       paginate_by=4),
        name='product_case_studies'),

    url(r'^product/case_studies/(?P<pk>\d+)/detail/$',
        views.CaseStudyDetail.as_view(template_name='skyhigh/product/case_studies/case_study_detail.html'),
        name='product_case_study_detail'),

    # Case Studies - Custom Pages

    url(r'^product/case_studies/case_study_cisco/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/product/case_studies/case_study_cisco.html'}, 
        name='case_study_cisco'),

    url(r'^product/case_studies/case_study_equinix/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/product/case_studies/case_study_equinix.html'}, 
        name='case_study_equinix'),

    url(r'^product/case_studies/case_study_torrance/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/product/case_studies/case_study_torrance.html'}, 
        name='case_study_torrance'),
                       
    # Partners

    url(r'^partners/overview/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/partners/partners_overview.html'}, 
        name='partners_overview'),

    url(r'^partners/apply/technology/$',
        views.TechnologyPartner.as_view(form_class=forms.TechnologyPartnerForm,
            template_name='skyhigh/partners/application/technology_partner_form.html',
            success_url='partners/application/thanks/'),
        name='partners_apply_technology'),
                       
    url(r'^partners/apply/csp/$',
        views.CloudServiceProviderPartner.as_view(form_class=forms.CloudServiceProviderForm,
            template_name='skyhigh/partners/application/cloud_service_provider_form.html',
            success_url='partners/application/thanks/'),
        name='partners_apply_csp'),

    url(r'^partners/apply/channel/$',
        views.ChannelPartner.as_view(form_class=forms.ChannelPartnerForm,
            template_name='skyhigh/partners/application/channel_partner_form.html',
            success_url='/partners/application/thanks/'),
        name='partners_apply_channel'),

    url(r'^secure/partners/complete/signup/$',
        views.CompletePartnerSignup.as_view(form_class=forms.CompleteUserProfileForm,
            template_name='skyhigh/partners/application/complete_partner_signup.html',
            success_url='/partners/application/thanks/'),
        name='complete_partner_signup'),

    url(r'^partners/application/already/submitted/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/partners/application/partnership_application_already_submitted.html'},
        name='partnership_application_already_submitted'),
                       
    url(r'^partners/application/thanks/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/partners/application/partnership_application_thanks.html'},
        name='partnership_application_thanks'),

    url(r'^partners/technology/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/placeholder.html'}, 
        name='partners_technology'),

    url(r'^partners/technology/integration/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/placeholder.html'}, 
        name='partners_technology_integration'),

    url(r'^partners/technology/resources/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/placeholder.html'}, 
        name='partners_technology_resources'),

    url(r'^partners/resellers/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/placeholder.html'}, 
        name='partners_resellers'),
                       
    url(r'^partners/resources/$',
        views.DealOverview.as_view(template_name='skyhigh/partners/partner_resources.html'),
        name='partners_resources'),

    url(r'^secure/partners/resources/deal/$',
        views.DealRequest.as_view(form_class=forms.DealForm,
            template_name='skyhigh/partners/deals/partner_deal_form.html',
            success_url='/partners/overview/'),
        name='partners_resources_deal'),

    url(r'^partners/resources/material/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/placeholder.html'}, 
        name='partners_resources_material'),

    url(r'^partners/resources/registration/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/placeholder.html'}, 
        name='partners_resources_registration'),
                       
    # News & Events

    url(r'^news/overview/$',
        views.NewsOverview.as_view(template_name='skyhigh/news/overview.html'),
        name='media_overview'),

    # Events

    url(r'^news/events/$',
        views.EventList.as_view(template_name='skyhigh/news/event_list.html'),
        name='media_events'),
                       
    # New layout for event page

    url(r'^events/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/news/event_list_new.html'}, 
        name='event'),

    # Media Coverage

    url(r'^news/coverage/$',
        views.MediaCoverageList.as_view(template_name='skyhigh/news/media_coverage_list.html'),
        name='media_coverage'),

    # Press Releases

    url(r'^news/press_releases/$',
        views.PressReleaseList.as_view(template_name='skyhigh/news/press_release_list.html',
                                       paginate_by=4),
        name='media_press_releases'),

    url(r'^news/press_releases/(?P<pk>\d+)/detail/$',
        views.PressReleaseDetail.as_view(template_name='skyhigh/news/press_release_detail.html'),
        name='media_press_releases_detail'),

    # Blog

    url(r'^blog/(?P<slug>[\w-]+)/$',
        views.BlogDetail.as_view(paginate_by=6, template_name='blog/blog_detail.html'),
        name='blog_detail'),

    (r'^blog/', include('unobase.blog.urls')),

    # Support

    # Forum

    (r'^support/forum/', include('unobase.forum.urls')),

    (r'^support/', include('unobase.support.urls')),
    
                       
    # Company

    url(r'^company/overview/$',
        views.LeadershipList.as_view(template_name='skyhigh/company/overview.html'), 
        name='company_overview'),
                       
    url(r'^company/leadership/$',
        views.LeadershipList.as_view(template_name='skyhigh/company/leadership/leadership_list.html',
                                     paginate_by=4),
        name='company_leadership'),

    url(r'^company/leadership/(?P<pk>\d+)/detail/$',
        views.LeadershipDetail.as_view(template_name='skyhigh/company/leadership/leadership_detail.html'),
        name='company_leadership_detail'),
                       
    url(r'^company/investors/$',
        views.InvestorList.as_view(template_name='skyhigh/company/investors/investor_list.html',
                                       paginate_by=4),
        name='company_investors'),

    url(r'^company/investors/(?P<pk>\d+)/detail/$',
        views.InvestorDetail.as_view(template_name='skyhigh/company/investors/investor_detail.html'),
        name='company_investor_detail'),

    url(r'^company/careers/$',
        views.CareerList.as_view(template_name='skyhigh/company/careers/career_list.html'),
        name='company_careers'),

    url(r'^secure/company/careers/apply/(?P<pk>\d+)/$',
        views.CareerApplication.as_view(form_class=forms.CareerApplicationForm,
            template_name='skyhigh/company/careers/application/career_application_form.html',
            success_url='/partners/overview/'),
        name='company_careers_apply'),

    url(r'^secure/company/careers/complete/signup/$',
        views.CompleteCareerSignup.as_view(form_class=forms.CompleteUserProfileForm,
            template_name='skyhigh/company/careers/application/complete_career_signup.html',
            success_url='/secure/accounts/login/'),
        name='company_careers_complete_signup'),

    url(r'^company/careers/application/already/submitted/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/company/careers/application/career_application_already_submitted.html'},
        name='company_careers_application_already_submitted'),

    url(r'^company/contact/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/company/contact.html'}, 
        name='company_contact'),

    url(r'^company/contact/details/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/placeholder.html'}, 
        name='company_contact_details'),

    url(r'^secure/company/contact/info_request/$',
        views.ContactInfoRequest.as_view(form_class=forms.ContactInfoRequestForm,
                                         template_name='skyhigh/company/contact_info_request_form.html'),
        name='company_contact_info_request'),

    url(r'^company/contact/info_request/complete/signup/$',
        views.CompleteContactInfoSignup.as_view(form_class=forms.CompleteUserProfileForm,
            template_name='skyhigh/company/complete_contact_info_signup.html',
            success_url='/secure/accounts/login/'),
        name='complete_contact_info_signup'),

    url(r'^company/contact/info_request/thanks/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/company/contact_info_request_thanks.html'}, 
        name='company_contact_info_request_thanks'),

    url(r'^company/video/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/company/video.html'}, 
        name='company_video'),

    # Search

    url(r'^search/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/search.html'}, 
        name='search'),


    # Mailer

    url(r'^mailer/$',
        simple_views.direct_to_template,
        {'template' : 'email/base.html'}, 
        name='mailer'),

    # Comments

    (r'^comments/', include('unobase.commenting.urls')),

    # Tagging

    (r'^tagging/', include('unobase.tagging.urls')),

    # Splash

    url(r'^splash/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/splash.html'}, 
        name='splash'),

    url(r'^splash/thanks/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/splash_thanks.html'}, 
        name='splash_thanks'),

    # Newsletter Signup

    url(r'^news/press_releases/$',
        views.PressReleaseList.as_view(template_name='skyhigh/news/press_release_list.html'),
        name='media_press_releases'),

    url(r'^newsletter/signup/$',
        views.NewsletterSignup.as_view(form_class=forms.NewsletterSignupForm),
        name='newsletter_signup'),

    url(r'^secure/newsletter/signup/$',
        views.NewsletterSignup.as_view(form_class=forms.NewsletterSignupForm),
        name='secure_newsletter_signup'),

    url(r'^secure/newsletter/complete/signup/$',
        views.CompleteNewsletterSignup.as_view(form_class=forms.CompleteUserProfileForm,
        template_name='skyhigh/complete_newsletter_signup.html',
        success_url='/secure/accounts/login/'),
        name='secure_complete_newsletter_signup'),

    url(r'^newsletter/signup/thanks/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/newsletter_signup_thanks.html'},
        name='newsletter_signup_thankyou'),

    url(r'^enterprise_grade/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/enterprise_grade.html'},
        name='enterprise_grade'),

    # Sitemap

    url(r'^sitemap.xml$', 
        simple_views.direct_to_template, 
        {'template' : 'sitemap.xml'}, 
        name='sitemap.xml'),

    # Campaigns

    url(r'^state-of-the-cloud-report/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/state_of_the_cloud_report.html'}, 
        name='state_of_the_cloud'),

    url(r'^company/healthcare/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/company/healthcare.html'}, 
        name='company_healthcare'),
                       
    url(r'^product/evaluation/30-in-30/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/campaigns/30-in-30.html'}, 
        name='campaign_30_in_30'),
                       
    url(r'^product/evaluation/30-in-30/register/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/campaigns/30-in-30-register.html'}, 
        name='campaign_30_in_30_register'),

    url(r'^product/evaluation/30-in-30/nexus/register/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/campaigns/30-in-30-nexus-register.html'}, 
        name='campaign_30_in_30_nexus_register'),

    url(r'^product/evaluation/30-in-30/tmmc/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/campaigns/tmmc-video.html'}, 
        name='campaign_30_in_30_tmmc_video'),

     url(r'^product/evaluation/30-in-30/tmmc/video/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/campaigns/tmmc-video-embed.html'}, 
        name='campaign_30_in_30_tmmc_video_embed'),

    url(r'^30-in-30/$',
        generic_views.RedirectView.as_view(
        url='/product/evaluation/30-in-30/'),
        name='30_in_30_vanity'),

#    url(r'^product/evaluation/demo/$',
#        simple_views.direct_to_template,
#        {'template' : 'skyhigh/campaigns/demo-14-august-2013.html'}, 
#        name='campaign_demo'),
#
#    url(r'^product/evaluation/demo/10-july-2013/$',
#        simple_views.direct_to_template,
#        {'template' : 'skyhigh/campaigns/demo-10-july-2013.html'}, 
#        name='campaign_demo_10_july_2013'),
#
#    url(r'^product/evaluation/demo/31-july-2013/$',
#        simple_views.direct_to_template,
#        {'template' : 'skyhigh/campaigns/demo-31-july-2013.html'}, 
#        name='campaign_demo_31_july_2013'),
#
#    url(r'^product/evaluation/demo/14-august-2013/$',
#        simple_views.direct_to_template,
#        {'template' : 'skyhigh/campaigns/demo-14-august-2013.html'}, 
#        name='campaign_demo_14_august_2013'),

    # New demo request landing page

    url(r'^product/evaluation/demo/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/campaigns/demo_request_landing.html'}, 
        name='campaign_demo'),
     

    url(r'^product/evaluation/csa/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/campaigns/csa.html'}, 
        name='campaign_csa'),

    url(r'^product/evaluation/csa/b/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/campaigns/csab.html'}, 
        name='campaign_csab'),

    url(r'^product/webinar/22-aug-2013/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/campaigns/landing-22-aug-2013.html'}, 
        name='landing-22-aug-2013'),

    url(r'^product/asset/13-aug-2013/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/campaigns/landing-13-aug-2013.html'}, 
        name='landing-13-aug-2013'),
                       
    # LANDING PAGES

    url(r'^product/asset/data-security/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/campaigns/asset-landing-data-security.html'}, 
        name='asset_landing_data_security'),  

    url(r'^product/asset/access-security/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/campaigns/asset-landing-access-security.html'}, 
        name='asset_landing_access_security'), 

    url(r'^product/asset/secure-brochure/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/campaigns/asset-landing-secure-brochure.html'}, 
        name='asset_landing_secure_brochure'),   

    url(r'^product/asset/data-protection/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/campaigns/asset-landing-data-protection.html'}, 
        name='asset_landing_data-protection'),                      
    
                       
    # Microsite pages

    url(r'^secure/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/microsite/landing.html'}, 
        name='micro_landing'),
                       
    # New pages

    url(r'^resources/$',
        views.Resources.as_view(template_name='skyhigh/resources/resources.html'),
        name='resources'),

    url(r'^resources/whitepapers/$',
        views.Whitepapers.as_view(template_name='skyhigh/resources/whitepapers.html'),
        name='resources_whitepapers'),

    url(r'^resources/datasheets/$',
        views.Datasheets.as_view(template_name='skyhigh/resources/datasheets.html'),
        name='resources_datasheets'),

    url(r'^resources/videos/$',
        views.Videos.as_view(template_name='skyhigh/resources/videos.html'),
        name='resources_videos'),

    url(r'^resources/webinars/$',
        views.Webinars.as_view(template_name='skyhigh/resources/webinars.html'),
        name='resources_webinars'),     

    #Redirects

    url(r'^product/evaluation/demo/14-august-2013/$',
        generic_views.RedirectView.as_view(
        url='/product/evaluation/'),
        name='demo_redir1'),

    url(r'^product/evaluation/demo/31-july-2013/$',
        generic_views.RedirectView.as_view(
        url='/product/evaluation/'),
        name='demo_redir2'),

    url(r'^product/evaluation/demo/19-june-2013/$',
        generic_views.RedirectView.as_view(
        url='/product/evaluation/'),
        name='demo_redir3'),

    url(r'^product/evaluation/demo/5-june-2013/$',
        generic_views.RedirectView.as_view(
        url='/product/evaluation/'),
        name='demo_redir4'),
                       
    url(r'^freeriskassessment/$',
        generic_views.RedirectView.as_view(
        url='/product/evaluation/'),
        name='free_risk_assessment'),

    url(r'^product-tour/$',
        generic_views.RedirectView.as_view(
        url='/cloud-security-product-tour/'),
        name='demo_redir5'),

)