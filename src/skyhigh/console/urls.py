'''
Created on 29 Dec 2012

@author: euan
'''
from django.conf.urls.defaults import patterns, include, url
from django.views.generic import simple as simple_views
from django.conf import settings

from skyhigh.console import forms, views
from skyhigh import models as skyhigh_models
from skyhigh import constants as skyhigh_constants

from unobase.blog import forms as blog_forms

urlpatterns = patterns('',

    # Statistics

    url(r'^$',
        views.ConsoleView.as_view(template_name='skyhigh/console/index.html'),
        name='console_index'),

    url(r'^statistics/overview/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/console/placeholder.html'}, 
        name='console_statistics_overview'),

    url(r'^statistics/kpis/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/console/placeholder.html'}, 
        name='console_statistics_kpis'),

    url(r'^statistics/averages/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/console/placeholder.html'}, 
        name='console_statistics_averages'),

    url(r'^statistics/totals/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/console/placeholder.html'}, 
        name='console_statistics_totals'),

    # Usage

    url(r'^usage/overview/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/console/placeholder.html'}, 
        name='console_usage_overview'),

    # Imports

    # Users

    url(r'^usage/user/import/$',
        views.Import.as_view(form_class=forms.UserImport,
            template_name='skyhigh/console/usage/users/user_import.html',
            success_url='/console/usage/user/import/'),
        name='console_usage_user_import'
    ),

    url(r'^import/user/template/download/$',
        views.DownloadFile.as_view(filepath='%s/skyhigh/templates/user_import_template.csv' % settings.STATIC_ROOT,
            filename='user_import_template.csv',
            mimetype='text/csv'),
        name='console_usage_user_import_template_download'
    ),

    # CSPs

    url(r'^usage/csp/import/$',
        views.Import.as_view(form_class=forms.CSPImport,
            template_name='skyhigh/console/usage/partners/csp/csp_import.html',
            success_url='/console/usage/csp/import/'),
        name='console_usage_csp_import'
    ),

    url(r'^import/csp/template/download/$',
        views.DownloadFile.as_view(filepath='%s/skyhigh/templates/csp_import_template.csv' % settings.STATIC_ROOT,
            filename='csp_import_template.csv',
            mimetype='text/csv'),
        name='console_usage_csp_import_template_download'
    ),
                       
    # SFTP Users
    
    url(r'^usage/sftp_user/create/$',
        views.SFTPUserCreate.as_view(form_class=forms.SFTPUser,
            template_name='skyhigh/console/usage/sftp_users/sftp_user_edit.html',
            success_url='/console/usage/sftp_user/%(id)d/detail/'),
        name='console_usage_sftp_user_create'),

    url(r'^usage/sftp_user/update/(?P<pk>\d+)/$',
        views.SFTPUserUpdate.as_view(form_class=forms.SFTPUser,
            template_name='skyhigh/console/usage/sftp_users/sftp_user_edit.html',
            success_url='/console/usage/sftp_user/%(id)d/detail/'),
        name='console_usage_sftp_user_update'),

    url(r'^usage/sftp_user/(?P<pk>\d+)/detail/$',
        views.SFTPUserDetail.as_view(template_name='skyhigh/console/usage/sftp_users/sftp_user_detail.html'),
        name='console_usage_sftp_user_detail'),

    url(r'^usage/sftp_user/delete/(?P<pk>\d+)/$',
        views.SFTPUserDelete.as_view(template_name='skyhigh/console/confirm_delete.html',
                                     success_url='/console/usage/sftp_user/list/'),
        name='console_usage_sftp_user_delete'),

    url(r'^usage/sftp_user/list/$',
        views.SFTPUserList.as_view(queryset=skyhigh_models.SFTPUser.objects.all(),
            paginate_by=20,
            template_name='skyhigh/console/usage/sftp_users/sftp_user_list.html'),
        name='console_usage_sftp_user_list'),

    # Users

    url(r'^usage/user/create/$',
        views.UserCreate.as_view(form_class=forms.User,
            template_name='skyhigh/console/usage/users/user_edit.html',
            success_url='/console/usage/user/%(id)d/detail/'),
        name='console_usage_user_create'),

    url(r'^usage/user/update/(?P<pk>\d+)/$',
        views.UserUpdate.as_view(form_class=forms.User,
            template_name='skyhigh/console/usage/users/user_edit.html',
            success_url='/console/usage/user/%(id)d/detail/'),
        name='console_usage_user_update'),

    url(r'^usage/user/(?P<pk>\d+)/detail/$',
        views.UserDetail.as_view(template_name='skyhigh/console/usage/users/user_detail.html'),
        name='console_usage_user_detail'),

    url(r'^usage/user/delete/(?P<pk>\d+)/$',
        views.UserDelete.as_view(template_name='skyhigh/console/confirm_delete.html',
                                 success_url='/console/usage/user/list/'),
        name='console_usage_user_delete'),

    url(r'^usage/user/list/$',
        views.UserList.as_view(queryset=skyhigh_models.Profile.objects.all(),
            template_name='skyhigh/console/usage/users/user_list.html',
            paginate_by=20),
        name='console_usage_user_list'),

    # Evaluators

    url(r'^usage/evaluator/create/$',
        views.UserCreate.as_view(form_class=forms.Evaluator,
            template_name='skyhigh/console/usage/evaluators/evaluator_edit.html',
            success_url='/console/usage/evaluator/%(id)d/detail/'),
        name='console_usage_evaluator_create'),

    url(r'^usage/evaluator/create/existing/user/list/$',
        views.UserList.as_view(queryset=skyhigh_models.Profile.objects.all(),
            template_name='skyhigh/console/usage/evaluators/existing_user_list.html',
            paginate_by=20),
        name='console_usage_evaluator_create_existing_user_list'),

    url(r'^usage/evaluator/create/existing/user/(?P<pk>\d+)/$',
        views.UserUpdate.as_view(form_class=forms.ExistingUserEvaluator,
            template_name='skyhigh/console/usage/evaluators/existing_user_evaluator_edit.html',
            success_url='/console/usage/evaluator/%(id)d/detail/'),
        name='console_usage_evaluator_create_existing_user'),

    url(r'^usage/evaluator/update/(?P<pk>\d+)/$',
        views.UserUpdate.as_view(form_class=forms.Evaluator,
            template_name='skyhigh/console/usage/evaluators/evaluator_edit.html',
            success_url='/console/usage/evaluator/%(id)d/detail/'),
        name='console_usage_evaluator_update'),

    url(r'^usage/evaluator/(?P<pk>\d+)/detail/$',
        views.UserDetail.as_view(template_name='skyhigh/console/usage/evaluators/evaluator_detail.html'),
        name='console_usage_evaluator_detail'),

    url(r'^usage/evaluator/delete/(?P<pk>\d+)/$',
        views.UserDelete.as_view(template_name='skyhigh/console/confirm_delete.html',
                                 success_url='/console/usage/evaluator/list/'),
        name='console_usage_evaluator_delete'),

    url(r'^usage/evaluator/list/$',
        views.UserList.as_view(queryset=skyhigh_models.Profile.objects.filter(evaluation_request__status=skyhigh_constants.PRODUCT_EVALUATION_STATUS_APPROVED),
            template_name='skyhigh/console/usage/evaluators/evaluator_list.html',
            paginate_by=20),
        name='console_usage_evaluator_list'),
                       
    # Log File Sample export
    
    url(r'^usage/evaluator/log/file/sample/export/(?P<pk>\d+)/$',
        views.LogFileSampleExport.as_view(
            template_name='skyhigh/console/usage/evaluators/log_file_sample_export.txt'),
        name='console_usage_evaluator_log_file_sample_export'),
                       
    url(r'^usage/evaluator/resend/log/file/sample/email/(?P<pk>\d+)/$',
        views.ResendLogFileSampleEmail.as_view(),
        name='console_usage_evaluator_resend_log_file_sample_email'),

    # Partners

    url(r'^usage/partner/create/(?P<type>technical|channel)/$',
        views.PartnerCreate.as_view(form_class=forms.Partner,
            template_name='skyhigh/console/usage/partners/partner_edit.html',
            success_url='/console/usage/partner/%(id)d/detail/'),
        name='console_usage_partner_create'),

    url(r'^usage/partner/update/(?P<pk>\d+)/$',
        views.PartnerUpdate.as_view(form_class=forms.Partner,
            template_name='skyhigh/console/usage/partners/partner_edit.html',
            success_url='/console/usage/partner/%(id)d/detail/'),
        name='console_usage_partner_update'),

    url(r'^usage/partner/(?P<pk>\d+)/detail/$',
        views.PartnerDetail.as_view(template_name='skyhigh/console/usage/partners/partner_detail.html'),
        name='console_usage_partner_detail'),

    url(r'^usage/partner/delete/(?P<pk>\d+)/$',
        views.PartnerDelete.as_view(template_name='skyhigh/console/confirm_delete.html',
                                    success_url='/console/usage/partner/list/'),
        name='console_usage_partner_delete'),

    url(r'^usage/partner/list/(?P<type>technical|channel)/$',
        views.PartnerList.as_view(template_name='skyhigh/console/usage/partners/partner_list.html',
                                  paginate_by=20),
        name='console_usage_partner_list'),

    # CSP Attributes

    url(r'^usage/partner/csp/attribute/list/(?P<pk>\d+)/$',
        views.CSPAttributeList.as_view(
            template_name='skyhigh/console/usage/partners/csp/csp_attribute_list.html'),
        name='console_usage_partner_csp_attribute_list'),

    url(r'^usage/partner/csp/attribute/list/export/(?P<pk>\d+)/$',
        views.CSPAttributeListExport.as_view(
            template_name='skyhigh/console/usage/partners/csp/csp_attribute_list_export.csv'),
        name='console_usage_partner_csp_attribute_list_export'),

    url(r'^usage/downloads/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/console/placeholder.html'}, 
        name='console_usage_downloads'),

    # Careers

    url(r'^usage/career/create/$',
        views.CareerCreate.as_view(
            form_class=forms.CareerForm,
            template_name='skyhigh/console/usage/careers/career_edit.html',
        ),
        name='console_usage_career_create'),

    url(r'^usage/career/update/(?P<pk>\d+)/$',
        views.CareerUpdate.as_view(
            form_class=forms.CareerForm,
            template_name='skyhigh/console/usage/careers/career_edit.html',
        ),
        name='console_usage_career_update'),

    url(r'^usage/career/delete/(?P<pk>\d+)/$',
        views.CareerDelete.as_view(
        ),
        name='console_usage_career_delete'),

    url(r'^usage/career/detail/(?P<pk>\d+)/$',
        views.CareerDetail.as_view(
            template_name='skyhigh/console/usage/careers/career_detail.html',
        ),
        name='console_usage_career_detail'),

    url(r'^usage/career/list/$',
        views.CareerList.as_view(
            template_name='skyhigh/console/usage/careers/career_list.html',
        ),
        name='console_usage_career_list'),

    # Career Applications

    url(r'^usage/career/application/(?P<pk>\d+)/detail/$',
        views.CareerApplicationDetail.as_view(
            template_name='skyhigh/console/usage/career_applications/career_application_detail.html',
        ),
        name='console_usage_career_application_detail'),

    url(r'^usage/career/application/list/$',
        views.CareerApplicationList.as_view(
            template_name='skyhigh/console/usage/career_applications/career_application_list.html',
        ),
        name='console_usage_career_application_list'),

    url(r'^usage/career/application/delete/(?P<pk>\d+)/$',
        views.CareerApplicationDelete.as_view(
        ),
        name='console_usage_career_application_delete'),
                       
    # Leaders
    
    url(r'^usage/leader/create/$',
        views.LeadershipCreate.as_view(form_class=forms.Leadership,
            template_name='skyhigh/console/usage/leadership/leader_edit.html',
            success_url='/console/usage/leader/%(id)d/detail/'),
        name='console_usage_leader_create'),

    url(r'^usage/leader/update/(?P<pk>\d+)/$',
        views.LeadershipUpdate.as_view(form_class=forms.Leadership,
            template_name='skyhigh/console/usage/leadership/leader_edit.html',
            success_url='/console/usage/leader/%(id)d/detail/'),
        name='console_usage_leader_update'),

    url(r'^usage/leader/(?P<pk>\d+)/detail/$',
        views.LeadershipDetail.as_view(template_name='skyhigh/console/usage/leadership/leader_detail.html'),
        name='console_usage_leader_detail'),

    url(r'^usage/leader/delete/(?P<pk>\d+)/$',
        views.LeadershipDelete.as_view(template_name='skyhigh/console/confirm_delete.html',
                                       success_url='/console/usage/leader/list/'),
        name='console_usage_leader_delete'),

    url(r'^usage/leader/list/$',
        views.LeadershipList.as_view(template_name='skyhigh/console/usage/leadership/leader_list.html',
        paginate_by=10),
        name='console_usage_leader_list'),
                       
    # Investors
    
    url(r'^usage/investor/create/$',
        views.InvestorCreate.as_view(form_class=forms.Investor,
            template_name='skyhigh/console/usage/investors/investor_edit.html',
            success_url='/console/usage/investor/%(id)d/detail/'),
        name='console_usage_investor_create'),

    url(r'^usage/investor/update/(?P<pk>\d+)/$',
        views.InvestorUpdate.as_view(form_class=forms.Investor,
            template_name='skyhigh/console/usage/investors/investor_edit.html',
            success_url='/console/usage/investor/%(id)d/detail/'),
        name='console_usage_investor_update'),

    url(r'^usage/investor/(?P<pk>\d+)/detail/$',
        views.InvestorDetail.as_view(template_name='skyhigh/console/usage/investors/investor_detail.html'),
        name='console_usage_investor_detail'),

    url(r'^usage/investor/delete/(?P<pk>\d+)/$',
        views.InvestorDelete.as_view(template_name='skyhigh/console/confirm_delete.html',
                                     success_url='/console/usage/investor/list/'),
        name='console_usage_investor_delete'),

    url(r'^usage/investor/list/$',
        views.InvestorList.as_view(template_name='skyhigh/console/usage/investors/investor_list.html',
        paginate_by=10),
        name='console_usage_investor_list'),
                       
    # Case Studies
    
    url(r'^usage/case_study/create/$',
        views.CaseStudyCreate.as_view(form_class=forms.CaseStudy,
            template_name='skyhigh/console/usage/case_studies/case_study_edit.html',
            success_url='/console/usage/case_study/%(id)d/detail/'),
        name='console_usage_case_study_create'),

    url(r'^usage/case_study/update/(?P<pk>\d+)/$',
        views.CaseStudyUpdate.as_view(form_class=forms.CaseStudy,
            template_name='skyhigh/console/usage/case_studies/case_study_edit.html',
            success_url='/console/usage/case_study/%(id)d/detail/'),
        name='console_usage_case_study_update'),

    url(r'^usage/case_study/(?P<pk>\d+)/detail/$',
        views.CaseStudyDetail.as_view(template_name='skyhigh/console/usage/case_studies/case_study_detail.html'),
        name='console_usage_case_study_detail'),

    url(r'^usage/case_study/delete/(?P<pk>\d+)/$',
        views.CaseStudyDelete.as_view(template_name='skyhigh/console/confirm_delete.html',
                                      success_url='/console/usage/case_study/list/'),
        name='console_usage_case_study_delete'),

    url(r'^usage/case_study/list/$',
        views.CaseStudyList.as_view(template_name='skyhigh/console/usage/case_studies/case_study_list.html',
        paginate_by=10),
        name='console_usage_case_study_list'),
                       
    # Configurable Emails

    url(r'^usage/configurable_email/update/(?P<pk>\d+)/$',
        views.ConfigurableEmailUpdate.as_view(form_class=forms.ConfigurableEmail,
            template_name='skyhigh/console/usage/configurable_emails/configurable_email_edit.html',
            success_url='/console/usage/configurable_email/%(id)d/detail/'),
        name='console_usage_configurable_email_update'),

    url(r'^usage/configurable_email/(?P<pk>\d+)/detail/$',
        views.ConfigurableEmailDetail.as_view(template_name='skyhigh/console/usage/configurable_emails/configurable_email_detail.html'),
        name='console_usage_configurable_email_detail'),

    url(r'^usage/configurable_email/delete/(?P<pk>\d+)/$',
        views.ConfigurableEmailDelete.as_view(template_name='skyhigh/console/confirm_delete.html',
                                              success_url='/console/usage/configurable_email/list/'),
        name='console_usage_configurable_email_delete'),

    url(r'^usage/configurable_email/list/$',
        views.ConfigurableEmailList.as_view(template_name='skyhigh/console/usage/configurable_emails/configurable_email_list.html',
        paginate_by=10),
        name='console_usage_configurable_email_list'),

    # News & Events Management

    url(r'^news/and/events/content/image/url/(?P<content_type>event|media_coverage)/(?P<pk>\d+)/$',
        views.ContentImageUrl.as_view(),
        name='console_news_and_events_content_image_url'),

    # Events

    url(r'^news/and/events/event/create/$',
        views.EventCreate.as_view(form_class=forms.Event,
                                  template_name='skyhigh/console/news_and_events/events/event_edit.html',
                                  success_url='/console/news/and/events/event/%(id)d/detail/'),
        name='console_news_and_events_event_create'),

    url(r'^news/and/events/event/update/(?P<pk>\d+)/$',
        views.EventUpdate.as_view(form_class=forms.Event,
            template_name='skyhigh/console/news_and_events/events/event_edit.html',
            success_url='/console/news/and/events/event/%(id)d/detail/'),
        name='console_news_and_events_event_update'),

    url(r'^news/and/events/event/(?P<pk>\d+)/detail/$',
        views.EventDetail.as_view(template_name='skyhigh/console/news_and_events/events/event_detail.html'),
        name='console_news_and_events_event_detail'),

    url(r'^news/and/events/event/delete/(?P<pk>\d+)/$',
        views.EventDelete.as_view(template_name='skyhigh/console/confirm_delete.html',
                                  success_url='/console/news/and/events/event/list/'),
        name='console_news_and_events_event_delete'),

    url(r'^news/and/events/event/list/$',
        views.EventsList.as_view(template_name='skyhigh/console/news_and_events/events/event_list.html',
                                 paginate_by=10),
        name='console_news_and_events_event_list'),

    # Media Coverage

    url(r'^news/and/events/media/coverage/create/$',
        views.MediaCoverageCreate.as_view(form_class=forms.MediaCoverage,
            template_name='skyhigh/console/news_and_events/media_coverage/media_coverage_edit.html',
            success_url='/console/news/and/events/media/coverage/%(id)d/detail/'),
        name='console_news_and_events_media_coverage_create'),

    url(r'^news/and/events/media/coverage/update/(?P<pk>\d+)/$',
        views.MediaCoverageUpdate.as_view(form_class=forms.MediaCoverage,
            template_name='skyhigh/console/news_and_events/media_coverage/media_coverage_edit.html',
            success_url='/console/news/and/events/media/coverage/%(id)d/detail/'),
        name='console_news_and_events_media_coverage_update'),

    url(r'^news/and/events/media/coverage/(?P<pk>\d+)/detail/$',
        views.MediaCoverageDetail.as_view(template_name='skyhigh/console/news_and_events/media_coverage/media_coverage_detail.html'),
        name='console_news_and_events_media_coverage_detail'),

    url(r'^news/and/events/media/coverage/delete/(?P<pk>\d+)/$',
        views.MediaCoverageDelete.as_view(template_name='skyhigh/console/confirm_delete.html',
                                          success_url='/console/news/and/events/media/coverage/list/'),
        name='console_news_and_events_media_coverage_delete'),

    url(r'^news/and/events/media/coverage/list/$',
        views.MediaCoverageList.as_view(template_name='skyhigh/console/news_and_events/media_coverage/media_coverage_list.html',
                                        paginate_by=10),
        name='console_news_and_events_media_coverage_list'),

    # Press Releases

    url(r'^news/and/events/press/release/create/$',
        views.PressReleasesCreate.as_view(form_class=forms.PressRelease,
            template_name='skyhigh/console/news_and_events/press_releases/press_release_edit.html',
            success_url='/console/news/and/events/press/release/%(id)d/detail/'),
        name='console_news_and_events_press_release_create'),

    url(r'^news/and/events/press/release/update/(?P<pk>\d+)/$',
        views.PressReleasesUpdate.as_view(form_class=forms.PressRelease,
            template_name='skyhigh/console/news_and_events/press_releases/press_release_edit.html',
            success_url='/console/news/and/events/media/coverage/%(id)d/detail/'),
        name='console_news_and_events_press_release_update'),

    url(r'^news/and/events/press/release/(?P<pk>\d+)/detail/$',
        views.PressReleasesDetail.as_view(template_name='skyhigh/console/news_and_events/press_releases/press_release_detail.html'),
        name='console_news_and_events_press_release_detail'),

    url(r'^news/and/events/press/release/delete/(?P<pk>\d+)/$',
        views.PressReleasesDelete.as_view(template_name='skyhigh/console/confirm_delete.html',
                                          success_url='/console/news/and/events/press/release/list/'),
        name='console_news_and_events_press_release_delete'),

    url(r'^news/and/events/press/release/list/$',
        views.PressReleasesList.as_view(template_name='skyhigh/console/news_and_events/press_releases/press_release_list.html',
        paginate_by=10),
        name='console_news_and_events_press_release_list'),

    # Blogs

#    url(r'^news/and/events/blog/create/$',
#        views.BlogCreate.as_view(form_class=blog_forms.Blog,
#            template_name='skyhigh/console/news_and_events/blogs/blog_edit.html',
#            success_url='/console/news/and/events/blog/%(id)d/detail/'),
#        name='console_news_and_events_blog_create'),
#
#    url(r'^news/and/events/blog/update/(?P<pk>\d+)/$',
#        views.BlogUpdate.as_view(form_class=blog_forms.Blog,
#            template_name='skyhigh/console/news_and_events/blogs/blog_edit.html',
#            success_url='/console/news/and/events/blog/%(id)d/detail/'),
#        name='console_news_and_events_blog_update'),

    url(r'^news/and/events/blog/(?P<slug>[\w-]+)/detail/$',
        views.BlogDetail.as_view(template_name='skyhigh/console/news_and_events/blogs/blog_detail.html'),
        name='console_news_and_events_blog_detail'),

#    url(r'^news/and/events/blog/delete/(?P<pk>\d+)/$',
#        views.BlogDelete.as_view(success_url='/console/news/and/events/blog/list/'),
#        name='console_news_and_events_blog_delete'),
#
#    url(r'^news/and/events/blog/list/$',
#        views.BlogList.as_view(template_name='skyhigh/console/news_and_events/blogs/blog_list.html'),
#        name='console_news_and_events_blog_list'),

    # Blog entries

    url(r'^news/and/events/blog/(?P<pk>\d+)/entry/create/$',
        views.BlogEntryCreate.as_view(form_class=blog_forms.BlogEntry,
            template_name='skyhigh/console/news_and_events/blogs/blog_entries/blog_entry_edit.html',
            success_url='/console/news/and/events/blog/entry/%(id)d/detail/'),
        name='console_news_and_events_blog_entry_create'),

    url(r'^news/and/events/blog/entry/update/(?P<pk>\d+)/$',
        views.BlogEntryUpdate.as_view(form_class=blog_forms.BlogEntry,
            template_name='skyhigh/console/news_and_events/blogs/blog_entries/blog_entry_edit.html',
            success_url='/console/news/and/events/blog/entry/%(id)d/detail/'),
        name='console_news_and_events_blog_entry_update'),

    url(r'^news/and/events/blog/entry/(?P<pk>\d+)/detail/$',
        views.BlogEntryDetail.as_view(template_name='skyhigh/console/news_and_events/blogs/blog_entries/blog_entry_detail.html'),
        name='console_news_and_events_blog_entry_detail'),

    url(r'^news/and/events/blog/entry/delete/(?P<pk>\d+)/$',
        views.BlogEntryDelete.as_view(template_name='skyhigh/console/confirm_delete.html',
                                      success_url='/console/news/and/events/blog/entry/list/'),
        name='console_news_and_events_blog_entry_delete'),


    # Messages

    url(r'^messages/(?P<pk>\d+)/detail/$',
        views.MessageDetail.as_view(template_name='skyhigh/console/messages/message_detail.html'),
        name='console_message_detail'),

    url(r'^messages/(?P<label>inbox|read|unread|responded)/$',
        views.MessageList.as_view(template_name='skyhigh/console/messages/message_list.html'),
        name='console_messages'),

    # Email Tracking

    (r'^email/tracking/', include('unobase.email_tracking.urls')),

    # Approvals

    url(r'^approvals/overview/$',
        simple_views.direct_to_template,
        {'template' : 'skyhigh/console/placeholder.html'}, 
        name='console_approvals_overview'),

    # Evaluation Approvals

    url(r'^approvals/evaluation/$',
        views.EvaluationApprovalList.as_view(template_name='skyhigh/console/evaluation/evaluation_approval_list.html',
                                             paginate_by=10),
        name='console_approvals_evaluation'),
                       
    url(r'^approvals/evaluation/detail/(?P<pk>\d+)/$',
        views.EvaluationApprovalDetail.as_view(template_name='skyhigh/console/evaluation/evaluation_approval_detail.html'),
        name='console_approvals_evaluation_detail'),

    url(r'^approvals/evaluation/action/(?P<action>approve|decline)/(?P<user_id>\d+)$',
        views.EvaluationApprovalAction.as_view(),
        name='console_approvals_evaluation_action'),

    # Partnership Approvals

    url(r'^approvals/partnership/$',
        views.PartnershipApprovalList.as_view(template_name='skyhigh/console/partners/partnership_approval_list.html',
                                              paginate_by=10),
        name='console_approvals_partnership'),

    url(r'^approvals/partnership/action/(?P<action>approve|decline)/(?P<user_id>\d+)$',
        views.PartnershipApprovalAction.as_view(),
        name='console_approvals_partnership_action'),
                       
)