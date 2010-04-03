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


from settings import *

from nntp import Server
from raw.models import NZB_REGEX, Group, Post

from raw import get_server
from raw import models


class Parser():
    """
    Class for parsing posts from a usenet group
    """
    
    def __init__(self, name):
        try:
            self.group = models.Group.objects.get(name=name)
        except Exception:
            group = Group()
            group.name = name
            group.save()
            self.group = group
        
        self.server = get_server()

    def parse(self):
        print self.server
        group = self.server.get_group(self.group.name)
        print group
        for id, subject in group[:10000]:
            #print subject[0], subject[1]
            match = NZB_REGEX.search(subject)
            if not match:
                # we can't do anything if we can't match the post to anything
                # else, right now only NZB are being accepted
                continue
            
            # we need the real id to reference across groups.
            article_id = self.server._server.stat(id)[2]
            
            try:
                post = Post.objects.get(nzb_id=id)
                # already exists, nothing to add
                return
            except Post.DoesNotExist:
                post = Post()
                post.first_id = id
                post.nzb_id = article_id
                post.subject = subject
            post.save()
            
            print post


if __name__ == '__main__':
    
    
    parser = Parser('alt.binaries.teevee')
    parser.parse()