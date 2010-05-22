import unittest
import re

from nntp import *


def suite():
    return unittest.TestSuite([
            unittest.TestLoader().loadTestsFromTestCase(GroupTest),            
        ])


class ServerProxy():
    """ imitation group for testing iterators """
    def group(self, name):
        return None, 10, 5, 14, name

    def xhdr(self, headers, posts):
        RE = re.compile('(\d+)\-(\d+)')
        match = RE.match(posts)
        start, end = match.groups()
        return None, range(int(start), int(end))


def c_groupiter():
    return GroupIterator(ServerProxy(), 'test.foo.bar')


class GroupTest(unittest.TestCase):
    """ tests for usenet groups """
    
    def setUp(self):
        self.tearDown()
    
    def tearDown(self):
        pass
    
    def test_iterate_all(self):
        iter = c_groupiter()
        self.assert_(len(iter)==10, len(iter))
        self.assert_(iter.first==5, iter.first)
        self.assert_(iter.last==14, iter.last)
        self.assert_(iter.count==10, iter.count)
        l = list(iter)
        self.assert_(l==range(5,16), l)
    
    def test_open_ended_slice(self):
        iter = c_groupiter()
        slice = list(iter[5:])
        self.assert_(len(slice)==5, slice)
        self.assert_(slice[0]==10, slice)
        self.assert_(slice[-1]==14, slice)
        l = list(slice)
        self.assert_(l==range(10,15), l)
    
    def test_open_begin_slice(self):
        iter = c_groupiter()
        slice = list(iter[:5])
        self.assert_(len(slice)==5, slice)
        self.assert_(slice[0]==5, slice)
        self.assert_(slice[-1]==9, slice)
        self.assert_(slice==range(5, 10))
    
    def test_slice(self):
        iter = c_groupiter()
        slice = list(iter[3:8])
        self.assert_(len(slice)==5, slice)
        self.assert_(slice[0]==8, slice)
        self.assert_(slice[-1]==12, slice)
        self.assert_(slice==range(8,13))