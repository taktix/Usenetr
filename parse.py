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
from raw.models import NZB_REGEX, Group, Post, ParseHistory

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
        """
        Parses the group held by this parser object
        """
        print self.server
        group = self.server.get_group(self.group.name)
        print group
        self._parse(group)
        
    def _parse(self, group):
        """
        parses a GroupIterator passed in.  This will create posts for all nzbs
        that are found.   Every 10000 posts a parse history object will also be
        created to ensure that if the process fails or is canceled a large
        history will not be lost.
        
        @returns id of last post that was parsed
        """
        count = 0
        start = None
        group_instance = Group.objects.get(name=group.name)
        for id, subject in group:
            try:
                if not start:
                    start = id
            
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
                    # already exists, only add group
                    if not post.groups.get(post=post).count():
                        posts.groups.add(self.group)
                    return
                    
                except Post.DoesNotExist:
                    post = Post()
                    post.first_id = id
                    post.nzb_id = article_id
                    post.subject = subject
                post.save()
                post.groups.add(self.group)
                #print post
            
            finally:
                # create history objects every 10000 posts
                count += 1
                if count == 50000:
                    print 'creating a history object'
                    history = ParseHistory()
                    history.start = start
                    history.end = id
                    history.group = group_instance
                    history.save()
                    start = id
                    count = 0
            
            
        
        #create a final history for whatever was at the end
        history = ParseHistory()
        history.start = start
        history.end = id
        history.group = group_instance
        history.save()
        start = id
        return id


if __name__ == '__main__':
    parser = Parser('alt.binaries.teevee')
    parser.parse()