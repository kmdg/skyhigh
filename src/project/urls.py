from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    (r'^', include('%s.urls' % settings.PROJECT_NAME)),
    
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^ckeditor/', include('ckeditor.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^accounts/', include('django.contrib.auth.urls')),
)

#------------------------------------------------------------------------------
# Django serves media
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$',
         'django.views.static.serve', 
         {'document_root' : settings.MEDIA_ROOT, 
          'show_indexes': True}
         ),
    )
