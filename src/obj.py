# Types which the user should never directly see
ERROR        = "<!error>"
RETURN_VALUE = "<!return value>"
FUNCTION     = "<!function>"

NEXT         = "<next>"
BREAK        = "<break>"

# Normal types
NUMBER   = "<number>"
BOOLEAN  = "<boolean>"
STRING   = "<string>"
CHAR     = "<char>"
ARRAY    = "<array>"
NULL     = "<null>"
BLOCK    = "<block>"
TUPLE    = "<tuple>"
OBJECT   = "<object>"
CLASS    = "<class>"
INIT     = "<init method>"
METH     = "<method>"
INSTANCE = "<instance>"

class InternalObject(object):
    def __eq__(self, other):
        return type(other) == type(self)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return ""

    def __repr__(self):
        return self.__str__()


class Collection(InternalObject):
    t = "<any collection>"
    
    def get_elements(self):
        return []


def compare(prop = "value"):
    return (lambda self, other: getattr(self, prop) == getattr(other, prop) if type(self) == type(other) else False)

def hasher():
    return (lambda self: hash(repr(self)))


class Error(InternalObject):
    t = ERROR

    """represents an error thrown in execution"""
    def __init__(self, msg, tag="GeneralError"):
        self.type = ERROR
        self.msg = msg
        self.tag = tag

    __eq__ = compare("msg")

    def __str__(self):
        return "%s: %s" % (self.tag, self.msg)


class ReturnValue(InternalObject):
    t = RETURN_VALUE
    
    """represents a value to be returned from a function"""
    def __init__(self, value):
        self.type = RETURN_VALUE
        self.value = value

    __eq__ = compare()

    def __str__(self):
        return str(self.value)


class Number(InternalObject):
    t = NUMBER
    
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
    t = BOOLEAN
    
    """a boolean object"""
    def __init__(self, value):
        self.type = BOOLEAN
        self.value = value

    __eq__ = compare()
    __hash__ = hasher()

    def __str__(self):
        return str(self.value).lower()


class String(Collection):
    t = STRING
    
    """a string object"""
    def __init__(self, value):
        self.type = STRING

        if type(value) == list:
            self.value = "".join(str(e) if type(e) != Char else str(e.value) for e in value)
        else:
            self.value = value

    __eq__ = compare()
    __hash__ = hasher()

    def __str__(self):
        return self.value

    def get_elements(self):
        return [Char(ch) for ch in list(self.value)]


class Char(InternalObject):
    t = CHAR
    
    """a character object"""
    def __init__(self, value):
        self.type = CHAR
        self.value = value

    __eq__ = compare()
    __hash__ = hasher()

    def __str__(self):
        return "'%s'" % self.value


class Tuple(Collection):
    t = TUPLE
    
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
    t = OBJECT
    
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

    def __getitem__(self, key):
        return self.pairs.get(String(key), Null())

    def __setitem__(self, key, val):
        self.pairs[String(key)] = val


class Null(InternalObject):
    t = NULL
    
    """the null object"""
    def __init__(self):
        self.type = NULL

    __hash__ = hasher()

    def __str__(self):
        return "null"


class Array(Collection):
    t = ARRAY
    
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
    t = FUNCTION
    
    """a function object"""
    def __init__(self, pattern, body, context):
        self.type = FUNCTION
        self.pattern = pattern # [id|param]
        self.body = body
        self.context = context

    def __str__(self):
        return "<function instance>"
    
    def on_call(self, args, ctx, enclosed):
        pass


class Block(InternalObject):
    t = BLOCK
    
    """a block object"""
    def __init__(self, params, body):
        self.type = BLOCK
        self.params = params
        self.body = body

    def __str__(self):
        return "<block instance>"


class Next(InternalObject):
    t = NEXT
    
    """result of the next; statement"""
    def __init__(self):
        self.type = NEXT

    def __str__(self):
        return "<next>"


class Break(InternalObject):
    t = BREAK
    
    """result of the break; statement"""
    def __init__(self):
        self.type = BREAK

    def __str__(self):
        return "<break>"


class InitMethod(InternalObject):
    t = INIT
    
    """an initialisation method of a class"""
    def __init__(self, fn):
        self.type = INIT
        self.fn = fn

    def __str__(self):
        return "<init method instance>"


class Method(InternalObject):
    t = METH
    
    """a normal method of a class"""
    def __init__(self, fn):
        self.type = METH
        self.fn = fn

    def __str__(self):
        return "<method instance>"


class Class(InternalObject):
    t = CLASS
    
    """a class object"""
    def __init__(self, name, parent, methods):
        self.type = CLASS
        self.name = name
        self.parent = parent
        self.methods = methods
        
    def __str__(self):
        return "<class '%s'>" % self.name
        
    def get_methods(self):
        methods = []
        
        if self.parent != None:
            methods = self.parent.get_methods()
        
        return [meth for meth in self.methods if isinstance(meth, Method)] + methods


class Instance(InternalObject):
    t = INSTANCE
    
    """an instance of a class """
    def __init__(self, base):
        self.type = INSTANCE
        self.base = base
        self.data = {}

    def __str__(self):
        return "<instance of %s>" % self.base
    
    def __getitem__(self, key):
        return self.data.get(key, Null())

    def __setitem__(self, key, val):
        self.data[key] = val
