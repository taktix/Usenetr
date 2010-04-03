import nntplib
import re
import yenc


class Group():
    """
    Wrapper class for a UseNet group.  This class is used for grabbing subjects
    from a group.  it implements some common functions for acting like an
    iterable list.
    """
    iter_step = 1000
    
    def __init__(self, server, name):
        self.server = server
        self.name = name
        resp, count, first, last, name = server.group(name)
        self.first = int(first)
        self.last = int(last)
        self.count = int(count)
    
    def __len__(self):
        return self.count
    
    def __getitem__(self, i):
        """ get a single subject """
        index = i+self.first
        self.server.xhdr('subject', '%s-%s' % (index, index))
    
    def __getslice__(self, i=0, j=None, step=None):
        """
        returns a generator that yields subjects.  The generator will query the
        server in increments of self.iter_step.  step is ignored
        """
        print '  Slicing: %s to %s' % (i, j)
        s = i+self.first
        e = j+self.first if j else self.count
        step = self.iter_step if e-j > self.iter_step else e-j
        for start in range(s, e, step):
            end = start+step if start+step < e else e
            print '   - inner slice: %s - %s' % (start-s, end-s)
            resp, subs = self.server.xhdr('subject', '%s-%s' % (start, end))
            for post in subs:
                yield post

    def __iter__(self):
        """
        Returns a generator for all subjects in this group.  This delegates to
        self.__getslice__
        """
        return self[:self.count]

    def __str__(self):
        return '%(name)s: start=%(first)s end=%(last)s count=%(count)s' % self.__dict__


class Server():
    def __init__(self, host, port=119, user=None, pw=None):
        self._server = nntplib.NNTP(host, port, user, pw)
        print self._server
    
    def get_group(self, name):
        print 'getting group: ', name
        return Group(self._server, name)
    
    def get_file(self, id):
        """
        Fetches a post and decodes it.  Note that this only works when the file
        contains the entire encoded file
        
        @param id - serverwide id.  Does not work with group id.
        """
        body = self._server.body(str(id))[3]
        
        # find start and end of encoded data
        start = 0
        end = 0
        regex = re.compile('^=(ybegin|ypart)')
        while regex.match(body[start]):
            start += 1
        regex = re.compile('^=yend')
        while regex.match(body[end-1]):
            end -= 1
        
        decoder = yenc.Decoder()
        decoder.feed(''.join(body[start:end]))
        return decoder.getDecoded()