class Context(object):
    """a context, aka a scope, which stores variables and functions"""
    def __init__(self):
        self.store = {}
        self.outer = None
        
    def enclose(self):
        ctx = Context()
        ctx.outer = self
        return ctx
        
    def __getitem__(self, key):
        obj = self.store.get(key, None)
        
        if obj == None and self.outer != None:
            obj = self.outer[key]
        
        return obj
        
    def __setitem__(self, key, val):
        if self.outer != None:
            if key in self.outer.store:
                self.outer[key] = val
                
        self.store[key] = val