'''
Created on 04 Jan 2013

@author: euan
'''
from django import forms
from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin, FlatpageForm
from django.contrib.flatpages.models import FlatPage

from ckeditor.widgets import CKEditorWidget

from skyhigh import models

class FlatPageAdminForm(FlatpageForm):
    content = forms.CharField(widget=CKEditorWidget())
    
class FlatPageAdmin(FlatPageAdmin):
    form = FlatPageAdminForm
    
try:
    admin.site.unregister(FlatPage)
except Exception, e:
    print e

admin.site.register(FlatPage, FlatPageAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'role',)
    fieldsets = (
        (None, {'fields': ('username', 'first_name', 'last_name', 'email',
                           'company', 'job_title', 'timezone',
                           'phone_number', 'mobile_number', 'address', 'city',
                           'state_province', 'zip_postal_code', 'country',
                           'role', 'image', 'maturation_score', 'after_login_url',
                           'newsletter_recipient', 'previous_email_addresses'
                            )}),
    )
    
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'object', 'content_object', 'timestamp')
    list_filter = ('user', 'action', 'timestamp')

class CSPAttributeInline(admin.TabularInline):
    model = models.CSPAttributeThrough

class CloudServiceProviderAdmin(admin.ModelAdmin):
    inlines = [
        CSPAttributeInline,
    ]
    search_fields = ('partnership',)

class CSPAttributeOptionInline(admin.TabularInline):
    model = models.CSPAttributeOption

class CSPAttributeAdmin(admin.ModelAdmin):
    inlines = [
        CSPAttributeOptionInline,
    ]
    list_display = ('si_number', 'category', 'name', 'description')
    list_filter = ('category',)    
    

admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.CSPAttribute, CSPAttributeAdmin)
admin.site.register(models.CloudServiceProvider, CloudServiceProviderAdmin)
admin.site.register(models.Reseller)
admin.site.register(models.Distributor)
admin.site.register(models.UserActivity, UserActivityAdmin)

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'external_link')
    list_filter = ('title', 'start_date', 'end_date')
    search_fields = ('title', 'content')

class MediaCoverageAdmin(admin.ModelAdmin):
    list_display = ('title', 'external_link', 'created', 'created_by')
    list_filter = ('title', 'created', 'created_by')
    search_fields = ('title', 'content')    

class PressReleaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'pdf', 'created', 'created_by')
    list_filter = ('title', 'created', 'created_by')
    search_fields = ('title', )
    
class PartnershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'request_date', 'status', 'type', 'modified')
    list_filter = ('user', 'status')
    search_fields = ('user',)

class CountryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    
class StateProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbr', 'country')
    search_fields = ('name',)
    
class ProductEvaluationAdmin(admin.ModelAdmin):
    list_display = ('user', 'request_date', 'status')
    list_filter = ('user', 'status')
    
class CSPAttributeAdmin(admin.ModelAdmin):
    list_display = ('si_number', 'category', 'name')
    list_filter = ('category', 'name')   

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'sent_date', 'status', 'message')
    list_filter = ('user', 'status')
    
class ConfigurableEmailAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'subject', 'content', 'plaintext_content',
                           'variables', 'internal_bccs', 'send_reason')}),
    )
    list_display = ('title', 'slug')

admin.site.register(models.Event, EventAdmin)
admin.site.register(models.Career)
admin.site.register(models.CareerApplication)
admin.site.register(models.MediaCoverage, MediaCoverageAdmin)
admin.site.register(models.PressRelease, PressReleaseAdmin)
admin.site.register(models.Partnership, PartnershipAdmin)
admin.site.register(models.Country, CountryAdmin)
admin.site.register(models.StateProvince, StateProvinceAdmin)
admin.site.register(models.ProductEvaluation, ProductEvaluationAdmin)
admin.site.register(models.ContactMessage, ContactMessageAdmin)
admin.site.register(models.Leader)
admin.site.register(models.Investor)
admin.site.register(models.Deal)
admin.site.register(models.CaseStudy)
admin.site.register(models.TargetVerticalFocus)
admin.site.register(models.SFTPUser)
admin.site.register(models.ConfigurableEmail, ConfigurableEmailAdmin)
admin.site.register(models.ConfigurableEmailVariable)
admin.site.register(models.ConfigurableEmailInternalBCC)
admin.site.register(models.Resource)