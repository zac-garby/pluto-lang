import ast
from builtin_fns import Builtin

class Context(object):
    """a context, aka a scope, which stores variables and functions"""
    def __init__(self):
        self.store = {}
        self.functions = []
        
        self.outer = None
        
    def enclose(self):
        ctx = Context()
        ctx.outer = self
        return ctx
    
    """args is a dictionary of strings to objects"""
    def enclose_with_args(self, args):
        ctx = self.enclose()
        
        for name in args:
            obj = args[name]
            ctx[name] = obj
                        
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
        
    def add_function(self, function):
        self.functions.append(function)
        
    def get_function(self, pattern):
        for func in self.functions:
            if len(pattern) != len(func.pattern):
                continue
                
            matched = True
                
            for i in range(len(pattern)):
                item = pattern[i]
                f_item = func.pattern[i]
                
                if type(item) == ast.Identifier and type(f_item) == ast.Identifier:
                    if item.value != f_item.value:
                        matched = False  
                elif not(type(item) == ast.Argument and type(f_item) == ast.Parameter):
                    matched = False
                    
            if matched:                
                return func
                
        for func in Builtin.builtins:
            if len(pattern) != len(func.pattern):
                continue
                
            matched = True
            
            for i in range(len(pattern)):
                item = pattern[i]
                f_item = func.pattern[i]
                
                if type(item) == ast.Identifier and f_item[0] != "$":
                    if item.value != f_item:
                        matched = False
                elif not(type(item) == ast.Argument and f_item[0] == "$"):
                    matched = False
                    
            if matched:
                return func
        
        return None