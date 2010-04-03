from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader

from models import Post


@login_required
def posts(request):
    posts = Post.objects.all()
    
    rc = RequestContext(request)
    return render_to_response('posts.html', {
        'posts':posts[:10]
    }, context_instance=rc)


@login_required    
def nfo(request):
    id = request.GET['id']
    post = Post.objects.get(id=id)
    return HttpResponse('<pre>'+post.nfo+'</pre>')
    
    
@login_required
def nzb_download(request, id):
    post = Post.objects.get(id=id)
    response = HttpResponse(mimetype='application/nzb')
    response['Content-Disposition'] = 'attachment; filename=%s.nzb' % id
    response.write(post.nzb)
    return response