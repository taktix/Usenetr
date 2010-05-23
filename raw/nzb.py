from xml.dom.minidom import Document

"""
example nzb

<nzb xmlns="http://www.newzbin.com/DTD/2003/nzb">
<file poster="tester" date="1253148619" subject="">
<groups>
<group>alt.testing</group>
</groups>
<segments>
<segment bytes="792927" number="1">post.id</segment>
<segment bytes="793062" number="2">post.id</segment>
</segments>
</file>
</nzb>
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
        doc = Document()
        nzb = doc.createElement("nzb")
        nzb.setAttribute("xmlns","http://www.newzbin.com/DTD/2003/nzb")
        doc.appendChild(nzb)
        
        for name, file in self.files.items():
            file_element = doc.createElement('file')
            file_element.setAttribute('subject', file.subject)
            nzb.appendChild(file_element)
            groups = doc.createElement('groups')
            for name in file.groups:
                group = doc.createElement('group')
                text = doc.createTextNode(name)
                group.appendChild(text)
                groups.appendChild(group)
            file_element.appendChild(groups)
            
            segments = doc.createElement('segments')
            for post in file.segments:
                segment = doc.createElement('segment')
                number, total = post.segment_id
                segment.setAttribute('number', str(number))
                text = doc.createTextNode(post.id)
                segment.appendChild(text)
                segments.appendChild(segment)
            file_element.appendChild(segments)
        
        return nzb.toxml()

    
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
        for group in post.groups.all():
            if not group.name in self.groups:
                self.groups.append(group.name)
        self.segments.append(post)

    def __len__(self):
        return len(self.segments)