import re

from django.db import models

from nntp import Server
from raw import get_server


NZB_REGEX = re.compile('\.nzb')
NFO_REGEX = re.compile('\.nfo')
NZB_NFO_REGEX = re.compile('\.nfo(.|\n)*?<segment.*number="1"\>(.*)\</segment>')

class Group(models.Model):
    """
    Describes a usenet group
    """
    name = models.CharField(max_length=64)


class ParseHistory(models.Model):
    """
    Describes parse history for a group.  This aids the parser by avoiding
    records you have already parsed.  There may be multiple segments that you
    have parsed in the past
    """
    group = models.ForeignKey(Group)
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
        Fetches the nfo post from usenet, decoding it.  This will cache the
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