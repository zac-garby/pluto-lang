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
CHAR    = "<char>"
ARRAY   = "<array>"
NULL    = "<null>"
BLOCK   = "<block>"
TUPLE   = "<tuple>"
OBJECT  = "<object>"

class InternalObject(object):
    def __eq__(self, other):
        return type(other) == type(self)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __str__(self):
        return ""
    
    __repr__ = __str__
    
    
class Collection(InternalObject):
    def get_elements(self):
        return []
    
    
def compare(prop = "value"):
    return (lambda self, other: getattr(self, prop) == getattr(other, prop) if type(self) == type(other) else False)
    
def hasher():
    return (lambda self: hash(repr(self)))


class Error(InternalObject):
    """represents an error thrown in execution"""
    def __init__(self, msg):
        self.type = ERROR
        self.msg = msg
    
    __eq__ = compare("msg")
    
    def __str__(self):
        return "ERROR: %s" % self.msg
        

class ReturnValue(InternalObject):
    """represents a value to be returned from a function"""
    def __init__(self, value):
        self.type = RETURN_VALUE
        self.value = value
    
    __eq__ = compare()
    
    def __str__(self):
        return str(self.value)
        

class Number(InternalObject):
    """represents a number object"""
    def __init__(self, value):
        self.type = NUMBER
        self.value = float(value)
        
    __eq__ = compare()
    __hash__ = hasher()
            
    def __str__(self):
        return str(self.value)
        
    def is_integer(self):
        return float(int(self.value)) == self.value
        
    def is_positive(self):
        return self.value >= 0
        
        
class Boolean(InternalObject):
    """a boolean object"""
    def __init__(self, value):
        self.type = BOOLEAN
        self.value = value
        
    __eq__ = compare()
    __hash__ = hasher()
    
    def __str__(self):
        return str(self.value).lower()
        
        
class String(Collection):
    """a string object"""
    def __init__(self, value):
        self.type = STRING
        
        if type(value) == list:
            self.value = "".join(str(e) for e in value)
        else:
            self.value = value
        
    __eq__ = compare()
    __hash__ = hasher()
    
    def __str__(self):
        return self.value

    def get_elements(self):
        return [Char(ch) for ch in list(self.value)]


class Char(InternalObject):
    """a character object"""
    def __init__(self, value):
        self.type = CHAR
        self.value = value
    
    __eq__ = compare()
    __hash__ = hasher()
    
    def __str__(self):
        return "'%s'" % self.value
    
        
class Tuple(Collection):
    """a tuple object"""
    def __init__(self, value):
        self.type = TUPLE
        self.value = value
    
    __eq__ = compare()
    __hash__ = hasher()
    
    def __str__(self):
        return "(%s)" % "".join(str(e) + ", " for e in self.value)[:-2]
        
    def get_elements(self):
        return self.value
        
        
class Object(InternalObject):
    """an object, similar to a dictionary in python"""
    def __init__(self, pairs):
        self.type = OBJECT
        self.pairs = dict(pairs)
        
    __eq__ = compare("pairs")
    __hash__ = hasher()
    
    def __str__(self):
        if len(self.pairs) == 0:
            return "[:]"
        else:
            return "[%s]" % "".join("%s: %s, " % (str(key), str(value)) for key, value in self.pairs.items())[:-2]
        
    def get_elements(self):
        return self.pairs.keys()
    
        
class Null(InternalObject):
    """the null object"""
    def __init__(self):
        self.type = NULL
        
    __hash__ = hasher()
    
    def __str__(self):
        return "null"
        
        
class Array(Collection):
    """an array object"""
    def __init__(self, elements):
        self.type = ARRAY
        self.elements = elements
        
    __eq__ = compare("elements")
    __hash__ = hasher()
            
    def __str__(self):
        return "[%s]" % "".join(str(e) + ", " for e in self.elements)[:-2]
        
    def get_elements(self):
        return self.elements
        
        
class Function(InternalObject):
    """a function object"""
    def __init__(self, pattern, body, context):
        self.type = FUNCTION
        self.pattern = pattern # [id|param]
        self.body = body
        self.context = context
    
    def __str__(self):
        return "<function instance>"
        
        
class Block(InternalObject):
    """a block object"""
    def __init__(self, params, body):
        self.type = BLOCK
        self.params = params
        self.body = body
        
    def __str__(self):
        return "<block instance>"
        
        
class Next(InternalObject):
    """result of the next; statement"""
    def __init__(self):
        self.type = NEXT
        
    def __str__(self):
        return "<next>"
        
        
class Break(InternalObject):
    """result of the break; statement"""
    def __init__(self):
        self.type = BREAK
        
    def __str__(self):
        return "<break>"