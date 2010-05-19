import unittest

from raw.models import *

def suite():
    return unittest.TestSuite([
            unittest.TestLoader().loadTestsFromTestCase(GroupTest),            
        ])

def c_group(**kwargs):
    """ helper for creating groups """
    group = Group()
    group.name = 'alt.testing'
    group.__dict__.update(kwargs)
    group.save()
    return group


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