# Types which the user should never directly see
ERROR = "<!error>"
RETURN_VALUE = "<!return value>"

# Normal types
NUMBER = "<number>"
BOOLEAN = "<boolean>"
STRING = "<string>"
ARRAY = "<array>"
NULL = "<null>"

class Object(object):
    def __eq__(self, other):
        return type(other) == type(self)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __str__(self):
        return ""
    
    __repr__ = __str__
    
    
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
        self.value = value
        
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
        
        
class String(Object):
    """a string object"""
    def __init__(self, value):
        self.type = STRING
        self.value = value
        
    __eq__ = compare()
    
    def __str__(self):
        return '"%s"' % self.value
        
        
class Null(Object):
    """the null object"""
    def __init__(self):
        self.type = NULL
        
    def __str__(self):
        return "null" 
        
        
class Array(Object):
    """an array object"""
    def __init__(self, elements):
        self.type = ARRAY
        self.elements = elements
        
    def __eq__(self, other):
        if type(other) != type(self):
            return False
        else:
            if len(self.elements) != len(other.elements):
                return False
                
            for i in range(len(self.elements)):
                if self.elements[i] != other.elements[i]:
                    return False
                    
            return True
            
    def __str__(self):
        return "[%s]" % "".join(str(e) + ", " for e in self.elements)[:-2]
    