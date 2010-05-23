import unittest

from raw.models import *

def suite():
    return unittest.TestSuite([
            unittest.TestLoader().loadTestsFromTestCase(GroupTest),
            unittest.TestLoader().loadTestsFromTestCase(PostTest),
        ])

def c_group(**kwargs):
    """ helper for creating groups """
    group = Group()
    group.name = 'alt.testing'
    group.__dict__.update(kwargs)
    group.save()
    return group

SUBJECT = subject = '[1337]-[FULL]-[#a.b.teevee@EFNet]-[ Testers.S08E23-E24.The.One.Where.I.prove.this.works.UNCUT.Taktix ]-[38/38] - "testers.8x23-taktix.vol31+04.par2" yEnc (%d/%d)'
def c_post(segment_id=1, segment_total=5, **kwargs):
    """ helper for creating posts """
    post = Post()    
    post.subject = SUBJECT % (segment_id, segment_total)
    post.__dict__.update(kwargs)
    post.save()
    return post


def c_history(**kwargs):
    history = ParseHistory()
    history.start = 1
    history.end = 10
    history.__dict__.update(kwargs)
    history.save()
    return history


class GroupTest(unittest.TestCase):
    """ tests for usenet groups """
    
    def setUp(self):
        self.tearDown()
    
    def tearDown(self):
        ParseHistory.objects.all().delete()
        Group.objects.all().delete()
    
    def test_consolidate_no_histories(self):
        """ tests nothing to conslidate """
        g = c_group()
        
    
    def test_consolidate_one_history(self):
        """ tests nothing to conslidate """
        g = c_group()
        c_history(group_id=g.id)
        g.consolidate_histories()
        self.assert_(g.histories.all().count()==1, g.histories.all().count())
        h = g.histories.all()[0]
        self.assert_(h.start==1, h.start)
        self.assert_(h.end==10, h.end)
    
    def test_consolidate_overlap_start(self):
        """ detects that an overlapping start is detected """
        g = c_group()
        c_history(group_id=g.id)
        c_history(group_id=g.id, start=5, end=20)
        g.consolidate_histories()
        self.assert_(g.histories.all().count()==1, g.histories.all().count())
        h = g.histories.all()[0]
        self.assert_(h.start==1, h.start)
        self.assert_(h.end==20, h.end)
        
    def test_consolidate_adjacent_start(self):
        """ tests that two exactly adjacent histories are detected """
        g = c_group()
        c_history(group_id=g.id)
        c_history(group_id=g.id, start=11, end=20)
        g.consolidate_histories()
        self.assert_(g.histories.all().count()==1, g.histories.all().count())
        h = g.histories.all()[0]
        self.assert_(h.start==1, h.start)
        self.assert_(h.end==20, h.end)
        
    def test_consolidate_overlap_end(self):
        """ tests that an end that was before the end of the first history is
        detected """
        g = c_group()
        c_history(group_id=g.id)
        c_history(group_id=g.id, start=4, end=6)
        g.consolidate_histories()
        self.assert_(g.histories.all().count()==1, g.histories.all().count())
        h = g.histories.all()[0]
        self.assert_(h.start==1, h.start)
        self.assert_(h.end==10, h.end)
        
        
    def test_consolidate_gap(self):
        """ tests that gaps are detected properly """
        g = c_group()
        c_history(group_id=g.id)
        c_history(group_id=g.id, start=15, end=20)
        c_history(group_id=g.id, start=21, end=30)
        g.consolidate_histories()
        self.assert_(g.histories.all().count()==2, g.histories.all().count())
        h = g.histories.all()[0]
        self.assert_(h.start==1, h.start)
        self.assert_(h.end==10, h.end)
        h = g.histories.all()[1]
        self.assert_(h.start==15, h.start)
        self.assert_(h.end==30, h.end)


class PostTest(unittest.TestCase):
    """ tests for posts """
    
    def setUp(self):
        self.tearDown()
    
    def tearDown(self):
        Post.objects.all().delete()
        Group.objects.all().delete()
    
    def test_get_filename(self):
        filename = c_post().filename
        self.assert_(filename=="testers.8x23-taktix.vol31+04.par2", filename)
        filename = c_post(segment_id=100, segment_total=1000).filename
        self.assert_(filename=="testers.8x23-taktix.vol31+04.par2", filename)
    
    def test_get_segment(self):
        segment_id, total = c_post().segment_id
        self.assert_(segment_id==1, segment_id)
        self.assert_(total==5, total)
        segment_id, total = c_post(segment_id=100, segment_total=1000).segment_id
        self.assert_(segment_id==100, segment_id)
        self.assert_(total==1000, total)
    
    def test_find_related(self):
        for i in range(5):
            post = c_post(segment_id=i)
        related = post.find_related()
        self.assert_(related.count()==5, related.count())
    