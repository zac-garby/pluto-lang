# Types which the user should never directly see
ERROR        = "<!error>"
RETURN_VALUE = "<!return value>"
FUNCTION     = "<!function>"

NEXT         = "<next>"
BREAK        = "<break>"

# Normal types
NUMBER  = "<number>"
BOOLEAN = "<boolean>"
STRING  = "<string>"
ARRAY   = "<array>"
NULL    = "<null>"
BLOCK   = "<block>"
TUPLE   = "<tuple>"

class Object(object):
    def __eq__(self, other):
        return type(other) == type(self)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __str__(self):
        return ""
    
    __repr__ = __str__
    
    
class Collection(Object):
    def get_elements(self):
        return []
    
    
def compare(prop = "value"):
    return (lambda self, other: getattr(self, prop) == getattr(other, prop) if type(self) == type(other) else False)


class Error(Object):
    """represents an error thrown in execution"""
    def __init__(self, msg):
        self.type = ERROR
        self.msg = msg
    
    __eq__ = compare("msg")
    
    def __str__(self):
        return "ERROR: %s" % self.msg
        

class ReturnValue(Object):
    """represents a value to be returned from a function"""
    def __init__(self, value):
        self.type = RETURN_VALUE
        self.value = value
    
    __eq__ = compare()
            
    
    def __str__(self):
        return str(self.value)
        

class Number(Object):
    """represents a number object"""
    def __init__(self, value):
        self.type = NUMBER
        self.value = float(value)
        
    __eq__ = compare()
            
    def __str__(self):
        return str(self.value)
        
    def is_integer(self):
        return float(int(self.value)) == self.value
        
    def is_positive(self):
        return self.value >= 0
        
        
class Boolean(Object):
    """a boolean object"""
    def __init__(self, value):
        self.type = BOOLEAN
        self.value = value
        
    __eq__ = compare()
    
    def __str__(self):
        return str(self.value).lower()
        
        
class String(Collection):
    """a string object"""
    def __init__(self, value):
        self.type = STRING
        self.value = value
        
    __eq__ = compare()
    
    def __str__(self):
        return "%s" % self.value
        
    def get_elements(self):
        return [obj.String(ch) for ch in list(self.value)]
        
        
class Tuple(Collection):
    """a tuple object"""
    def __init__(self, value):
        self.type = TUPLE
        self.value = value
    
    __eq__ = compare()
    
    def __str__(self):
        return "(%s)" % "".join(str(e) + ", " for e in self.value)[:-2]
        
    def get_elements(self):
        return self.value
    
        
class Null(Object):
    """the null object"""
    def __init__(self):
        self.type = NULL
        
    def __str__(self):
        return "null" 
        
        
class Array(Collection):
    """an array object"""
    def __init__(self, elements):
        self.type = ARRAY
        self.elements = elements
        
    __eq__ = compare("elements")
            
    def __str__(self):
        return "[%s]" % "".join(str(e) + ", " for e in self.elements)[:-2]
        
    def get_elements(self):
        return self.elements
        
        
class Function(Object):
    """a function object"""
    def __init__(self, pattern, body, context):
        self.type = FUNCTION
        self.pattern = pattern # [id|param]
        self.body = body
        self.context = context
    
    def __str__(self):
        return "<function instance>"
        
        
class Block(Object):
    """a block object"""
    def __init__(self, params, body):
        self.type = BLOCK
        self.params = params
        self.body = body
        
    def __str__(self):
        return "<block instance>"
        
        
class Next(Object):
    """result of the next; statement"""
    def __init__(self):
        self.type = NEXT
        
    def __str__(self):
        return "<next>"
        
        
class Break(Object):
    """result of the break; statement"""
    def __init__(self):
        self.type = BREAK
        
    def __str__(self):
        return "<break>"