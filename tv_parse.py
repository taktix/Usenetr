#!/usr/bin/env python
if __name__ == '__main__':
    import sys
    import os

    #python magic to add the current directory to the pythonpath
    sys.path.append(os.getcwd())

    # ==========================================================
    # Setup django environment 
    # ==========================================================
    if not os.environ.has_key('DJANGO_SETTINGS_MODULE'):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
    # ==========================================================
    # Done setting up django environment

import re


from raw.models import Post
from tv.models import TV

TEEVEE = re.compile('\[\d+\]\-\[\w+\]\-\[\#a\.b\.teevee@EFNet\]\-\[ (.*) \]')


# regex's that will be used in this order for parsing out titles from tv shows
titles = [
        re.compile('[ "]([\w\._-]*).[sS](\d{2}[eE]\d{2})'),           # S00E00
        re.compile('[ "]([\w\._-]*).[sS](\d{1,2}\.?[dD]\d{1,2})'),    # S00D00
        re.compile('[ "]([\w\.]*).(\d{4}[\.-]\d{2}[\.-]\d{2})'),      # YYYY-MM-DD
        re.compile('[ "]([\w\._-]*).(\d{1,2}x\d{1,2})'),              # 0x00
        re.compile('[ "]([\w\._-]*).([eE]\d{2})'),                    # E00
        re.compile('[ "]([\w\._-]*).(\d{2}[-.]\d{2}[-.]\d{2})'),      # DD-MM-YY
        re.compile('[ "]([\w\._-]*).(\d{4})')                         # YYYY
    ]


for post in Post.objects.all():
    for regex in titles:
        match = regex.search(post.subject)
        if match:
            try:
                tv = TV.objects.get(post_ptr=post.id)
            except TV.DoesNotExist:
                tv = TV()
                tv.post_ptr = post
                tv.__dict__.update(post.__dict__)
                tv.title = '%s - %s' % match.groups() 
                tv.save()
            
            break
    if not match:
        print 'no match: ', post.subject 