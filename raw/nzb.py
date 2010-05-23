

"""
<nzb xmlns="http://www.newzbin.com/DTD/2003/nzb">
<file poster="teevee@4u.tv (teevee)" date="1253148619" subject="[1854]-[FULL]-[#a.b.teevee@EFNet]-[ Friends.S08E23-E24.The.One.Where.Rachel.Has.A.Baby.UNCUT.DVDRip.XviD-SAiNTS ]-[38/38] - &#34;friends.8x23-saints.vol31+04.par2&#34; yEnc (1/7)">
<groups>
<group>alt.binaries.multimedia</group>
<group>alt.binaries.teevee</group>
</groups>
<segments>
<segment bytes="792927" number="1">1253148619.30301.1@news.astraweb.com</segment>
<segment bytes="793062" number="2">1253148619.34830.2@news.astraweb.com</segment>
<segment bytes="792907" number="3">1253148619.37062.3@news.astraweb.com</segment>
<segment bytes="792852" number="4">1253148619.38625.4@news.astraweb.com</segment>
<segment bytes="792820" number="5">1253148619.39987.5@news.astraweb.com</segment>
<segment bytes="792772" number="6">1253148619.41607.6@news.astraweb.com</segment>
<segment bytes="41743" number="7">1253148619.46308.7@news.astraweb.com</segment>
</segments>
</file>
"""


class NZB(object):
    """ NZB builder """
    
    def __init__(self, query=None):
        """ builds an nzb out of a query for posts """
        files = {}
        
        if query:
            for post in query:
                filename = post.filename
                if filename in files:
                    files[filename].add(post)
                else:
                    files[filename] = File(post)
        self.files = files
    
    def to_xml(self):
        pass
    
    def __len__(self):
        return len(self.files)
    
    def __contains__(self, k):
        return k in self.files
    
    def __getitem__(self, k):
        return self.files[k]


class File():
    def __init__(self, post):
        self.filename = post.filename
        self.subject = post.subject

        self.groups = []
        self.segments = []
        self.add(post)
    
    def add(self, post):
        """
        Adds a Post (segment) to this file
        """
        """
        for group in post.groups:
            if not group.name in self.groups():
                self.groups.append(group.name)
        """
        self.segments.append(post)

    def __len__(self):
        return len(self.segments)