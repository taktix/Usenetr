from django.conf.urls.defaults import *
import settings
from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    #authentication
    (r'^accounts/login/$', login),
    (r'^accounts/logout/$', logout, {'next_page':'/'}),

    # admin site
    (r'^admin/', include(admin.site.urls)),

    (r'^/*', include('raw.urls')),
    (r'^tv/*', include('tv.urls')),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':  settings.MEDIA_ROOT}),
)


