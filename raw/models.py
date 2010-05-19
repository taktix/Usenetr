import re

from django.db import models

from nntp import Server, GroupIterator
from raw import get_server


NZB_REGEX = re.compile('\.nzb')
NFO_REGEX = re.compile('\.nfo')
NZB_NFO_REGEX = re.compile('\.nfo(.|\n)*?<segment.*number="1"\>(.*)\</segment>')

class Group(models.Model):
    """
    Describes a usenet group
    """
    name = models.CharField(max_length=64)

    def consolidate_histories(self):
        """ consolidates consecutive history objects into a single history
        object for quicker searching """
        
        histories = self.histories.all().order_by('start','end')
        if len(histories) < 2:
            # need at least 2 history objects to consolidate them
            return
        
        current = histories[0]
        for history in histories[1:]:
            if history.start <= current.end+1:
                if history.end > current.end:
                    current.end = history.end
                current.save()
                history.delete()
            else:
                #no overlap, switch to new current
                current = history

    def get_last(self):
        """
        Returns the last id parsed in this group.  This only checks the parse
        history objects associated with this group.  Its possible there are posts
        that were parsed and created but a history object never created.
        """
        histories = self.histories.all().order_by('-end')
        if histories.count():
            return histories[0].end
        return None

    def parse_new(self):
        """ parses group starting with the newest post """
        server = get_server()
        iterator = server.get_group(self.name)
        parser = Parser(self.name, server)
        last = self.get_last()
        
        if last == None:
            print '%s Parsing starting with: %s ' % (self.name, 1)
            last = parser._parse(iterator)
            start = 1
        else:
            start = last+1
            print '%s Parsing starting with: %s ' % (self.name, start)
            last = parser._parse(iterator[start-iterator.first:])
            
        # create history of what was just parsed, then consolidate it with
        # existing parse histories
        self.consolidate_histories()
    
    def parse(self, all=False):
        """ parses group starting with the first post """
        server = get_server()
        iterator = GroupIterator(server, self.name)
        parser = Parser(self.name)
        
        if all:
            last = parser._parse(iterator)
        else:
            last = parser._parse(iterator)
            
        # create history of what was just parsed, then consolidate it with
        # existing parse histories
        self.consolidate_histories()
    
    def reverse_parse(self, all=False):
        """
        Parses group starting from the newest post.  This is used for building
        the index with the most recent content first.  Useful for when you are
        concerned with something recent, and don't want to spend the time
        indexing from the beginning (for instance giganews retains 600 days)
        """
        pass


class ParseHistory(models.Model):
    """
    Describes parse history for a group.  This aids the parser by avoiding
    records you have already parsed.  There may be multiple segments that you
    have parsed in the past, skipping these can save large amounts of time
    """
    group = models.ForeignKey(Group, related_name="histories")
    start = models.IntegerField()
    end = models.IntegerField()
    

class Post(models.Model):
    """
    Describes a raw binary post.  This describes info for finding the related
    files.
    
    uid - identify used by the usenet group to identify parts of a post
    first_id - id of the first post found for this binary
    nzb_id - id of the nzb for this post
    nfo_id - id of the nfo for this post
    
    subject - subject of the post found.  This is one of the following with this
              priority:
                    1) The nzb post subject
                    2) The nfo post subject
                    3) The first post subject found
    """
    groups = models.ManyToManyField(Group)
    #uid = models.IntegerField()
    first_id = models.IntegerField()
    nzb_id = models.CharField(max_length=32, null=True)
    nfo_id = models.CharField(max_length=32, null=True)
    subject = models.CharField(max_length=180)
    time = models.DateTimeField(null=True)
    
    _nzb = None
    _nfo = None
    
    def __str__(self):
        return str(self.__dict__)
    
    def get_nfo(self):
        """
        Fetches the nfo post from usenet, decoding it.  This will cache the
        post if needed
        """
        if not self.nfo_id:
            # no nfo id, try and get it from the nzb if we have it
            if self.nzb_id:
                nzb = self.nzb
                match = NZB_NFO_REGEX.search(self.nzb)
                if match:
                    # resolve the nfo_id and save it
                    self.nfo_id = '<%s>' % match.groups()[1]
                    self.save()
                    return self.get_nfo()
            return None
            
        if self._nfo:
            return self._nfo
        
        server = get_server()
        self._nfo = server.get_file(self.nfo_id)
        return self._nfo
    nfo = property(get_nfo)
    
    def get_nzb(self):
        """
        Fetches the nzb post from usenet, decoding it.  This will cache the
        post if needed
        """
        if not self.nzb_id:
            return None
        if self._nzb:
            return self._nzb
        
        server = get_server()
        self._nzb = server.get_file(self.nzb_id)
        return self._nzb
    nzb = property(get_nzb)
    
    
class Parser():
    """
    Class for parsing posts from a usenet group
    """
    
    def __init__(self, name, server=None):
        try:
            self.group = models.Group.objects.get(name=name)
        except Exception:
            group = Group()
            group.name = name
            group.save()
            self.group = group
        
        self.server = server if server else get_server()

    def parse(self):
        """
        Parses the group held by this parser object
        """
        print self.server
        group = self.server.get_group(self.group.name)
        print group
        self._parse(group)
        
    def _parse(self, iterator):
        """
        parses a GroupIterator passed in.  This will create posts for all nzbs
        that are found.   Every 10000 posts a parse history object will also be
        created to ensure that if the process fails or is canceled a large
        history will not be lost.
        
        @returns id of last post that was parsed
        """
        count = 0
        start = None
        group = self.group
        for id, subject in iterator:
            
            if not start:
                start = id
        
            #print subject[0], subject[1]
            match = NZB_REGEX.search(subject)
            if not match:
                # we can't do anything if we can't match the post to anything
                # else, right now only NZB are being accepted
                count += 1
                if count == 1000:
                    print 'creating a history object (%s-%s)' % (start, id)
                    history = ParseHistory()
                    history.start = start
                    history.end = id
                    history.group = group
                    history.save()
                    print group.get_last()
                    start = id
                    count = 0
                continue
            
            # we need the real id to reference across groups.
            article_id = self.server._server.stat(id)[2]
            
            try:
                post = Post.objects.get(nzb_id=id)
                # already exists, only add group
                if not post.groups.get(post=post).count():
                    posts.groups.add(group)
                return
                
            except Post.DoesNotExist:
                post = Post()
                post.first_id = id
                post.nzb_id = article_id
                post.subject = subject
            post.save()
            post.groups.add(group)
            #print post
            
            
            # create history objects every 10000 posts
            count += 1
            if count == 1000:
                print 'creating a history object (%s-%s)' % (start, id)
                history = ParseHistory()
                history.start = start
                history.end = id
                history.group = group
                history.save()
                print group.get_last()
                start = id
                count = 0
        
        
        #create a final history for whatever was at the end
        history = ParseHistory()
        history.start = start
        history.end = id
        history.group = group
        history.save()
        start = id
        return id