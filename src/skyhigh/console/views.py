'''
Created on 29 Dec 2012

@author: euan
'''

from django.views import generic as generic_views
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from skyhigh import models as skyhigh_models
from skyhigh import constants as skyhigh_constants
from skyhigh import forms as skyhigh_forms
from skyhigh import automatic_emails
from skyhigh.utils import respond_with_json
from skyhigh import constants
from skyhigh.api import product as api_product

from unobase import constants as unobase_constants
from unobase import views as unobase_views
from unobase import mixins as unobase_mixins

from unobase.blog import models as blog_models

import forms

class AdminMixin(unobase_mixins.RoleCheckMixin):
    role_required = constants.ROLE_CHOICE_ADMIN
    raise_exception = False

class ConsoleView(AdminMixin, generic_views.TemplateView):
    pass

# Approvals

# Partnership Approvals

class PartnershipApprovalList(AdminMixin, unobase_mixins.FilterMixin, generic_views.ListView):
    
    allowed_filters = {
        'first_name': 'user__first_name__icontains',
        'last_name': 'user__first_name__icontains',
        'email': 'user__email__icontains',
        }

    def get_context_data(self, **kwargs):
        context = super(PartnershipApprovalList, self).get_context_data(**kwargs)
        context['filter_form'] = forms.PendingEvaluatorFilter(self.request.GET)
        return context

    def get_queryset(self):
        return skyhigh_models.Partnership.objects.filter(status=constants.PARTNERSHIP_REQUEST_STATUS_PENDING)\
            .filter(**self.get_queryset_filters())

class PartnershipApprovalAction(AdminMixin, generic_views.View):

    def get(self, request, *args, **kwargs):
        action = kwargs['action']
        user_id = kwargs['user_id']

        partnership = skyhigh_models.Partnership.objects.get(user__pk=user_id)

        if action == 'approve':
            partnership.status = constants.PARTNERSHIP_REQUEST_STATUS_APPROVED

        elif action == 'decline':
            partnership.status = constants.PARTNERSHIP_REQUEST_STATUS_DECLINED
            
        partnership.modified_by = request.user

        partnership.save()

        if request.is_ajax():
            return respond_with_json({'status': 'success'})

        return HttpResponseRedirect(request.META['HTTP_REFERER'])

# Evaluation Approvals

class EvaluationApprovalList(AdminMixin, unobase_mixins.FilterMixin, generic_views.ListView):
    
    allowed_filters = {
        'first_name': 'user__first_name__icontains',
        'last_name': 'user__first_name__icontains',
        'email': 'user__email__icontains',
        }

    def get_context_data(self, **kwargs):
        context = super(EvaluationApprovalList, self).get_context_data(**kwargs)
        context['filter_form'] = forms.PendingEvaluatorFilter(self.request.GET)
        return context

    def get_queryset(self):
        return skyhigh_models.ProductEvaluation.objects.filter(status=constants.PRODUCT_EVALUATION_STATUS_PENDING)\
            .filter(**self.get_queryset_filters())
    
class EvaluationApprovalDetail(AdminMixin, generic_views.DetailView):

    def get_object(self):
        return skyhigh_models.ProductEvaluation.objects.get(pk=self.kwargs['pk'])

class EvaluationApprovalAction(AdminMixin, generic_views.View):

    def get(self, request, *args, **kwargs):
        action = kwargs['action']
        user_id = kwargs['user_id']

        evaluation = skyhigh_models.ProductEvaluation.objects.get(user__pk=user_id)
        
        evaluation.modified_by = request.user

        if action == 'approve':
            evaluation.status = constants.PRODUCT_EVALUATION_STATUS_APPROVED
            evaluation.save()

            api_product.create_evaluation_account(evaluation.user)

        elif action == 'decline':
            evaluation.status = constants.PRODUCT_EVALUATION_STATUS_DECLINED
            evaluation.save()

        if request.is_ajax():
            return respond_with_json({'status': 'success'})

        return HttpResponseRedirect(request.META['HTTP_REFERER'])

# Usage

# SFTP Users

class SFTPUserCreate(AdminMixin, generic_views.CreateView):
    pass

class SFTPUserUpdate(AdminMixin, generic_views.UpdateView):

    def get_queryset(self):
        return skyhigh_models.SFTPUser.objects.all()

class SFTPUserDetail(AdminMixin, generic_views.DetailView):

    def get_object(self):
        return get_object_or_404(skyhigh_models.SFTPUser,
            pk=self.kwargs['pk'])

class SFTPUserDelete(AdminMixin, generic_views.DeleteView):

    def get_queryset(self):
        return skyhigh_models.SFTPUser.objects.all()

class SFTPUserList(AdminMixin, unobase_mixins.FilterMixin, generic_views.ListView):

    allowed_filters = {
        'username': 'username__icontains',
        }

    def get_context_data(self, **kwargs):
        context = super(SFTPUserList, self).get_context_data(**kwargs)
        context['filter_form'] = forms.SFTPUserFilter(self.request.GET)
        return context

# Users

class UserCreate(AdminMixin, generic_views.CreateView):

    def get_initial(self):
        return {'user' : self.request.user }

class UserUpdate(AdminMixin, generic_views.UpdateView):

    def get_initial(self):
        return {'user' : self.request.user }

    def get_queryset(self):
        return skyhigh_models.Profile.objects.all()

class UserDetail(AdminMixin, generic_views.DetailView):
    
    def get_context_data(self, **kwargs):
        csp_attribute_list = []
        for csp_attribute in skyhigh_models.CSPAttribute.objects.all().order_by('si_number'):
            try:
                value = csp_attribute.csp_rel.get(cloud_service_provider__partnership__user_id=self.kwargs['pk']).value
            except skyhigh_models.CSPAttributeThrough.DoesNotExist:
                value = None

            csp_attribute_list.append({'si_number': csp_attribute.si_number,
                                       'category': csp_attribute.get_category_display(),
                                       'name': csp_attribute.name,
                                       'value': value})

        context = {
            'csp_attribute_list': csp_attribute_list,
        }
        context.update(kwargs)
        return super(UserDetail, self).get_context_data(**context)

    def get_object(self):
        return get_object_or_404(skyhigh_models.Profile,
            pk=self.kwargs['pk'])

class UserDelete(AdminMixin, generic_views.DeleteView):

    def get_queryset(self):
        return skyhigh_models.Profile.objects.all()

class UserList(AdminMixin, unobase_mixins.FilterMixin, generic_views.ListView):

    allowed_filters = {
        'first_name': 'first_name__icontains',
        'last_name': 'last_name__icontains',
        'email': 'email__icontains',
        'company': 'company__icontains',
        'job_title': 'job_title__icontains'
        }

    def get_context_data(self, **kwargs):
        context = super(UserList, self).get_context_data(**kwargs)
        context['filter_form'] = forms.UserFilter(self.request.GET)
        return context

# Imports

class Import(AdminMixin, generic_views.FormView):
    def form_valid(self, form):
        form.save(request=self.request)
        return super(Import, self).form_valid(form)

# Download file

class DownloadFile(AdminMixin, generic_views.View):

    filepath = None
    filename = None
    mimetype = None

    def get(self, request):
        response = HttpResponse(mimetype=self.mimetype)
        response['Content-Disposition'] = 'attachment;filename=%s' % self.filename
        response.write(open(self.filepath, 'rb').read())
        return response

# Partners

class PartnerCreate(AdminMixin, generic_views.CreateView):

    def get_initial(self):
        return {'user' : self.request.user,
                'type': self.kwargs['type']}

class PartnerUpdate(AdminMixin, generic_views.UpdateView):

    def get_initial(self):
        return {'user' : self.request.user }

    def get_queryset(self):
        return skyhigh_models.Profile.objects.all()

class PartnerDetail(AdminMixin, generic_views.DetailView):

    def get_object(self):
        return get_object_or_404(skyhigh_models.Profile,
            pk=self.kwargs['pk'])

class PartnerDelete(AdminMixin, generic_views.DeleteView):

    def get_queryset(self):
        return skyhigh_models.Profile.objects.all()

class PartnerList(AdminMixin, unobase_mixins.FilterMixin, generic_views.ListView):
    allowed_filters = {
        'first_name': 'first_name__icontains',
        'last_name': 'last_name__icontains',
        'email': 'email__icontains',
        'company': 'company__icontains',
        'job_title': 'job_title__icontains'
    }

    def get_context_data(self, **kwargs):
        context = {
            'type': self.kwargs['type'],
            'filter_form': forms.UserFilter(self.request.GET)
        }
        context.update(kwargs)
        return super(PartnerList, self).get_context_data(**context)

    def get_queryset(self):
        type = self.kwargs['type']

        if type == 'channel':
            return skyhigh_models.Profile.objects.filter(partnership__status=skyhigh_constants.PARTNERSHIP_REQUEST_STATUS_APPROVED,
                partnership__type=skyhigh_constants.PARTNER_TYPE_CHANNEL).filter(**self.get_queryset_filters())


        return skyhigh_models.Profile.objects.filter(partnership__status=skyhigh_constants.PARTNERSHIP_REQUEST_STATUS_APPROVED,
            partnership__type=skyhigh_constants.PARTNER_TYPE_TECHNOLOGY).filter(**self.get_queryset_filters())

# CSP Attributes

class CSPAttributeList(AdminMixin, generic_views.TemplateView):

    def get_context_data(self, **kwargs):
        csp_attribute_list = []
        for csp_attribute in skyhigh_models.CSPAttribute.objects.all().order_by('si_number'):
            try:
                value = csp_attribute.csp_rel.get(cloud_service_provider__partnership__user_id=self.kwargs['pk']).value
            except skyhigh_models.CSPAttributeThrough.DoesNotExist:
                value = None

            csp_attribute_list.append({'si_number': csp_attribute.si_number,
                                       'category': csp_attribute.get_category_display(),
                                       'name': csp_attribute.name,
                                       'options': csp_attribute.options.all(),
                                       'value': value})

        try:
            form_errors = self.form.errors
        except AttributeError:
            form_errors = None

        context = {
            'object_list': csp_attribute_list,
            'form_errors': form_errors
        }
        context.update(kwargs)
        return super(CSPAttributeList, self).get_context_data(**context)

    def post(self, request, *args, **kwargs):
        self.form = forms.ConsoleCSPAttributesForm(request.POST, initial={'profile': skyhigh_models.Profile.objects.get(pk=self.kwargs['pk'])})

        if self.form.is_valid():
            self.form.save()

        return self.get(request, *args, **kwargs)


class CSPAttributeListExport(AdminMixin, generic_views.ListView):

    def get_queryset(self):
        return skyhigh_models.CSPAttributeThrough.objects.filter(
            cloud_service_provider__partnership__user_id=self.kwargs['pk']).order_by('cloud_service_provider_attribute__si_number')

    def render_to_response(self, context, **kwargs):
        response = super(CSPAttributeListExport, self).render_to_response(
            context,
            content_type='text/csv',
            **kwargs
        )
        response['Content-Disposition'] = 'attachment; filename="csp-attribute-export.csv"'
        return response
    
class LogFileSampleExport(AdminMixin, generic_views.DetailView):

    def get_object(self):
        return skyhigh_models.ProductEvaluation.objects.get(user_id=self.kwargs['pk'])

    def render_to_response(self, context, **kwargs):
        response = super(LogFileSampleExport, self).render_to_response(
            context,
            content_type='text/plain',
            **kwargs
        )
        response['Content-Disposition'] = 'attachment; filename="log-file-sample.txt"'
        return response
    
class ResendLogFileSampleEmail(AdminMixin, generic_views.View):
    
    def get(self, request, *args, **kwargs):
        product_evaluation = skyhigh_models.ProductEvaluation.objects.get(user_id=self.kwargs['pk'])
        
        automatic_emails.email_static_page_uploaded.delay(product_evaluation.user.id, product_evaluation.log_file_sample)
        
        messages.success(self.request, 'Log File Sample email has been resent.')
        
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

# Career

class CareerCreate(AdminMixin, generic_views.CreateView):
    def get_initial(self):
        return {'user': self.request.user}

    def get_success_url(self):
        return reverse('console_usage_career_detail', args=[self.object.pk])

class CareerUpdate(AdminMixin, generic_views.UpdateView):
    def get_initial(self):
        return {'user': self.request.user}

    def get_queryset(self):
        return skyhigh_models.Career.objects.all()

    def get_success_url(self):
        return reverse('console_usage_career_detail', args=[self.object.pk])

class CareerDelete(AdminMixin, generic_views.DeleteView):
    def get_queryset(self):
        return skyhigh_models.Career.objects.all()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.state = unobase_constants.STATE_DELETED
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

    def get_success_url(self):
        return reverse('console_usage_career_list')

class CareerDetail(AdminMixin, generic_views.DetailView):
    def get_object(self):
        return get_object_or_404(skyhigh_models.Career, pk=self.kwargs['pk'])

class CareerList(AdminMixin, generic_views.ListView):
    def get_queryset(self):
        return skyhigh_models.Career.objects.all()

# Career Application

class CareerApplicationDetail(AdminMixin, generic_views.DetailView):
    def get_object(self):
        return get_object_or_404(skyhigh_models.CareerApplication, pk=self.kwargs['pk'])

class CareerApplicationList(AdminMixin, unobase_mixins.FilterMixin, generic_views.ListView):
    allowed_filters = {
        'first_name': 'user__profile__first_name__icontains',
        'last_name': 'user__profile__last_name__icontains',
        'email': 'user__email__icontains',
    }

    def get_context_data(self, **kwargs):
        context = {
            'filter_form': forms.UserFilter(self.request.GET)
        }
        context.update(kwargs)
        return super(CareerApplicationList, self).get_context_data(**context)

    def get_queryset(self):
        return skyhigh_models.CareerApplication.objects.all().filter(**self.get_queryset_filters())

class CareerApplicationDelete(AdminMixin, generic_views.DeleteView):
    def get_queryset(self):
        return skyhigh_models.CareerApplication.objects.all()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

    def get_success_url(self):
        return reverse('career_application_list')

# Get image url
class ContentImageUrl(AdminMixin, generic_views.View):

    def get(self, request, *args, **kwargs):

        content_type = kwargs['content_type']

        if content_type == 'event':
            content_object = get_object_or_404(skyhigh_models.Event, pk=kwargs['pk'])
        elif content_type == 'media_coverage':
            content_object = get_object_or_404(skyhigh_models.MediaCoverage, pk=kwargs['pk'])

        return respond_with_json({'url': content_object.get_120x120_url()})

# Events

class EventCreate(AdminMixin, generic_views.CreateView):

    def get_initial(self):
        return {'user' : self.request.user }

class EventUpdate(AdminMixin, generic_views.UpdateView):

    def get_initial(self):
        return {'user' : self.request.user }

    def get_queryset(self):
        return skyhigh_models.Event.objects.all()

class EventDetail(AdminMixin, generic_views.DetailView):

    def get_object(self):
        return get_object_or_404(skyhigh_models.Event,
            pk=self.kwargs['pk'])

class EventDelete(AdminMixin, generic_views.DeleteView):

    def get_queryset(self):
        return skyhigh_models.Event.objects.all()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.state = unobase_constants.STATE_DELETED
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

class EventsList(AdminMixin, generic_views.ListView):

    def get_queryset(self):
#        return skyhigh_models.Event.objects.all()
        return skyhigh_models.Event.objects.all().exclude(state=unobase_constants.STATE_DELETED)

# Media Coverage

class MediaCoverageCreate(AdminMixin, generic_views.CreateView):

    def get_initial(self):
        return {'user' : self.request.user }

class MediaCoverageUpdate(AdminMixin, generic_views.UpdateView):

    def get_initial(self):
        return {'user' : self.request.user }

    def get_queryset(self):
        return skyhigh_models.MediaCoverage.objects.all()

class MediaCoverageDetail(AdminMixin, generic_views.DetailView):

    def get_object(self):
        return get_object_or_404(skyhigh_models.MediaCoverage,
            pk=self.kwargs['pk'])

class MediaCoverageDelete(AdminMixin, generic_views.DeleteView):

    def get_queryset(self):
        return skyhigh_models.MediaCoverage.objects.all()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.state = unobase_constants.STATE_DELETED
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

class MediaCoverageList(AdminMixin, generic_views.ListView):

    def get_queryset(self):
        return skyhigh_models.MediaCoverage.objects.exclude(state=unobase_constants.STATE_DELETED)

# Press Releases

class PressReleasesCreate(AdminMixin, generic_views.CreateView):

    def get_initial(self):
        return {'user' : self.request.user }

class PressReleasesUpdate(AdminMixin, generic_views.UpdateView):

    def get_initial(self):
        return {'user' : self.request.user }

    def get_queryset(self):
        return skyhigh_models.PressRelease.objects.exclude(state=unobase_constants.STATE_DELETED)

class PressReleasesDetail(AdminMixin, generic_views.DetailView):

    def get_object(self):
        return get_object_or_404(skyhigh_models.PressRelease,
            pk=self.kwargs['pk'])

class PressReleasesDelete(AdminMixin, generic_views.DeleteView):

    def get_queryset(self):
        return skyhigh_models.PressRelease.objects.all()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.state = unobase_constants.STATE_DELETED
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

class PressReleasesList(AdminMixin, generic_views.ListView):

    def get_queryset(self):
        return skyhigh_models.PressRelease.objects.all().exclude(state=unobase_constants.STATE_DELETED)
    
# Leadership

class LeadershipCreate(AdminMixin, generic_views.CreateView):

    def get_initial(self):
        return {'user' : self.request.user }

class LeadershipUpdate(AdminMixin, generic_views.UpdateView):

    def get_initial(self):
        return {'user' : self.request.user }

    def get_queryset(self):
        return skyhigh_models.Leader.objects.all()

class LeadershipDetail(AdminMixin, generic_views.DetailView):

    def get_object(self):
        return get_object_or_404(skyhigh_models.Leader,
            pk=self.kwargs['pk'])

class LeadershipDelete(AdminMixin, generic_views.DeleteView):

    def get_queryset(self):
        return skyhigh_models.Leader.objects.all()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.state = unobase_constants.STATE_DELETED
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

class LeadershipList(AdminMixin, generic_views.ListView):

    def get_queryset(self):
        return skyhigh_models.Leader.objects.all().exclude(state=unobase_constants.STATE_DELETED)
    
# Investors

class InvestorCreate(AdminMixin, generic_views.CreateView):

    def get_initial(self):
        return {'user' : self.request.user }

class InvestorUpdate(AdminMixin, generic_views.UpdateView):

    def get_initial(self):
        return {'user' : self.request.user }

    def get_queryset(self):
        return skyhigh_models.Investor.objects.all()

class InvestorDetail(AdminMixin, generic_views.DetailView):

    def get_object(self):
        return get_object_or_404(skyhigh_models.Investor,
            pk=self.kwargs['pk'])

class InvestorDelete(AdminMixin, generic_views.DeleteView):

    def get_queryset(self):
        return skyhigh_models.Investor.objects.all()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.state = unobase_constants.STATE_DELETED
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

class InvestorList(AdminMixin, generic_views.ListView):

    def get_queryset(self):
        return skyhigh_models.Investor.objects.all().exclude(state=unobase_constants.STATE_DELETED)
    
# Case Studies

class CaseStudyCreate(AdminMixin, generic_views.CreateView):

    def get_initial(self):
        return {'user' : self.request.user }

class CaseStudyUpdate(AdminMixin, generic_views.UpdateView):

    def get_initial(self):
        return {'user' : self.request.user }

    def get_queryset(self):
        return skyhigh_models.CaseStudy.objects.all()

class CaseStudyDetail(AdminMixin, generic_views.DetailView):

    def get_object(self):
        return get_object_or_404(skyhigh_models.CaseStudy,
            pk=self.kwargs['pk'])

class CaseStudyDelete(AdminMixin, generic_views.DeleteView):

    def get_queryset(self):
        return skyhigh_models.CaseStudy.objects.all()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.state = unobase_constants.STATE_DELETED
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

class CaseStudyList(AdminMixin, generic_views.ListView):

    def get_queryset(self):
        return skyhigh_models.CaseStudy.objects.all().exclude(state=unobase_constants.STATE_DELETED)
    
# Configurable Emails

class ConfigurableEmailUpdate(AdminMixin, generic_views.UpdateView):

    def get_initial(self):
        return {'user' : self.request.user }

    def get_queryset(self):
        return skyhigh_models.ConfigurableEmail.objects.all()

class ConfigurableEmailDetail(AdminMixin, generic_views.DetailView):

    def get_object(self):
        return get_object_or_404(skyhigh_models.ConfigurableEmail,
            pk=self.kwargs['pk'])

class ConfigurableEmailDelete(AdminMixin, generic_views.DeleteView):

    def get_queryset(self):
        return skyhigh_models.ConfigurableEmail.objects.all()

class ConfigurableEmailList(AdminMixin, generic_views.ListView):

    def get_queryset(self):
        return skyhigh_models.ConfigurableEmail.objects.all()

# Blogs

class BlogCreate(AdminMixin, generic_views.CreateView):

    def get_initial(self):
        return {'user' : self.request.user }

class BlogUpdate(AdminMixin, generic_views.UpdateView):

    def get_initial(self):
        return {'user' : self.request.user }

    def get_queryset(self):
        return blog_models.Blog.objects.all()

class BlogDetail(AdminMixin, unobase_views.ListWithDetailView):

    def get_object(self):
        return get_object_or_404(blog_models.Blog,
            slug=self.kwargs['slug'])

    def get_queryset(self):
        return blog_models.BlogEntry.objects.filter(blog=self.object)

class BlogDelete(AdminMixin, generic_views.DeleteView):

    def get_queryset(self):
        return blog_models.Blog.objects.all()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.state = unobase_constants.STATE_DELETED
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

class BlogList(AdminMixin, generic_views.ListView):

    def get_queryset(self):
        return blog_models.Blog.objects.all()

# Blog Entries

class BlogEntryCreate(AdminMixin, generic_views.CreateView):

    def get_initial(self):
        return {'user' : self.request.user,
                'blog_id': self.kwargs['pk']}

class BlogEntryUpdate(AdminMixin, generic_views.UpdateView):

    def get_initial(self):
        return {'user' : self.request.user }

    def get_queryset(self):
        return blog_models.BlogEntry.objects.all()

class BlogEntryDetail(AdminMixin, generic_views.DetailView):

    def get_object(self):
        return get_object_or_404(blog_models.BlogEntry,
            pk=self.kwargs['pk'])

class BlogEntryDelete(AdminMixin, generic_views.DeleteView):

    def get_queryset(self):
        return blog_models.BlogEntry.objects.all()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.state = unobase_constants.STATE_DELETED
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get(self, *args, **kwargs):
        return self.delete(*args, **kwargs)

class BlogEntryList(AdminMixin, generic_views.ListView):

    def get_queryset(self):
        return blog_models.BlogEntry.objects.all()

# Messages

class MessageDetail(AdminMixin, generic_views.DetailView):

    def get_context_data(self, **kwargs):
        context = {
            'form': forms.ContactMessageReplyForm(kwargs['object'])
        }
        context.update(kwargs)
        return super(MessageDetail, self).get_context_data(**context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = forms.ContactMessageReplyForm(contact_message=self.object, user=request.user, data=request.POST)

        if form.is_valid():
            form.send_mail()
            return HttpResponseRedirect('/console/messages/inbox/')

        return self.get(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if self.object.status == constants.CONTACT_MESSAGE_STATUS_UNREAD:
            self.object.status = constants.CONTACT_MESSAGE_STATUS_READ
            self.object.modified_by = request.user
            self.object.save()

        return self.render_to_response(context)

    def get_object(self):
        return get_object_or_404(skyhigh_models.ContactMessage,
            pk=self.kwargs['pk'])

class MessageList(AdminMixin, generic_views.ListView):

    def get_context_data(self, **kwargs):
        context = {
            'label': self.kwargs['label']
        }
        context.update(kwargs)
        return super(MessageList, self).get_context_data(**context)

    def get_queryset(self):
        label = self.kwargs['label']

        if label == 'inbox':
            return skyhigh_models.ContactMessage.objects.all()

        if label == 'read':
            return skyhigh_models.ContactMessage.objects.filter(status__in=[constants.CONTACT_MESSAGE_STATUS_READ, constants.CONTACT_MESSAGE_STATUS_RESPONDED])

        if label == 'unread':
            return skyhigh_models.ContactMessage.objects.filter(status=constants.CONTACT_MESSAGE_STATUS_UNREAD)

        if label == 'responded':
            return skyhigh_models.ContactMessage.objects.filter(status=constants.CONTACT_MESSAGE_STATUS_RESPONDED)


