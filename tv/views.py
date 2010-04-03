from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from raw.views import paginate
from models import TV


@login_required
def tv(request):
    posts, page, pages = paginate(request, TV.objects.all())

    return render_to_response('tv.html', {
        'posts':posts,
        'page_start':(page-1)*25,
        'pages':pages
    }, context_instance=RequestContext(request))
