import object as obj
import ast
from evaluator import NULL, TRUE, FALSE


class Builtin(object):
    builtins = []
    
    """a builtin function"""
    def __init__(self, pattern, fn):
        self.pattern = pattern # e.g. ["print", "$obj"]
        self.fn = fn           # fn(args) where args is a dictionary
        
        Builtin.builtins.append(self)


def builtin(pattern):
    def builtin_gen(fn):
        Builtin(pattern, fn)
        return fn
        
    return builtin_gen  
    
    
## Builtin definitions ##  

@builtin(["print", "$obj"])
def print_builtin(args, context):
    print(args["obj"])
    return NULL
