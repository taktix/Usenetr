from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns('',    
    (r'^$', posts),
    (r'^nfo/$', nfo),
    (r'^nzb/(\d+)/$', nzb_download),
    (r'^related/(.*)/$', find_related),
    (r'^search/', search)
)