from django.conf.urls import patterns, include, url

import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^kuvat/', include('kuvat.urls')),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        })
)

urlpatterns += patterns('',
    (),
)