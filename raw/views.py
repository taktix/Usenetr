from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader


from models import Post


@login_required
def posts(request):
    posts, page, pages = paginate(request, Post.objects.all())

    return render_to_response('posts.html', {
        'posts':posts,
        'page_start':(page-1)*25,
        'pages':pages
    }, context_instance=RequestContext(request))


def paginate(request, posts):
    """Paginates a list of posts"""
    paginator = Paginator(posts, 25) # Show 25 posts per page

    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        posts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page = paginator.num_pages
        posts = paginator.page(page)

    # digg style pagination list
    pages = get_page_list(paginator, page)
    
    return posts, page, pages


def get_page_list(paginator, page=1):
    """
    Generate a list of pages used choose from to jump quickly to a page

    This generates a list that shows:
        * if near the start/end, up to 10 pages from the start/end
        * if in the middle first two and last two pages in addition to the
          +/- 5 from the current page
       * if num_pages<10 - only one list of pages is shown
       * if num_pages==11 then the list is statically generated because this
         list size results in wierd results for the standard logic that generates
         the lists.
    """

    if paginator.num_pages < 11:
        # special case: only one list of values
        pages = (range(1,paginator.num_pages+1),)
    elif paginator.num_pages == 11:
        # special case: lists are static
        pages = ([1,2,3,4,5,6,7,8,9,10], None, [11])
    else:
        # normal case
        start = [i for i in range(1, 11 if page < 8 and page < paginator.num_pages-6 else 3)]
        middle = [i for i in range(page-5,page+5)] if page > 7 and page < paginator.num_pages-6 else None
        end = [i for i in range(paginator.num_pages-(1 if page < paginator.num_pages-6 else 9), paginator.num_pages+1)]
        pages = (start, middle, end)

    return pages


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


@login_required
def search(request):
    regex = '.'.join(request.GET['clause'].split(' '))
    query = Post.objects.filter(subject__regex=regex)
    
    posts, page, pages = paginate(request, query)

    return render_to_response('posts.html', {
        'posts':posts,
        'page_start':(page-1)*25,
        'pages':pages
    }, context_instance=RequestContext(request))