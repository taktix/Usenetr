class Composite():
    """ regex comprised of multiple sub-regex """
    def __init__(self, regexes):
        self.regexes = regexes
    
    def match(self, s):
        for regex in self.regexes:
            match = regex.match(s)
            if match:
                return match
    
    def search(self, s):
        for regex in self.regexes:
            match = regex.search(s)
            if match:
                return match
    