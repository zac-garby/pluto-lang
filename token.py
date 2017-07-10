# etc...
EOF     = "EOF"
ILLEGAL = "illegal"

# Literals
NUM    = "number"
STR    = "string"
ID     = "identifier"
PARAM  = "param"

# Punctuation
PLUS    = "plus"          # +
MINUS   = "minus"         # -
STAR    = "star"          # *
SLASH   = "slash"         # /
BSLASH  = "backslash"     # \
LPAREN  = "lparen"        # (
RPAREN  = "rparen"        # )
LT      = "less-than"     # <
GT      = "greater-than"  # >
LBRACE  = "lbrace"        # {
RBRACE  = "rbrace"        # }
LSQUARE = "lsquare"       # [
RSQUARE = "rsquare"       # ]
SEMI    = "semi"          # ;
EQ      = "equal"         # ==
N_EQ    = "not-equal"     # !=
OR      = "or"            # ||
AND     = "and"           # and
B_OR    = "bitwise-or"    # or
B_AND   = "bitwise-and"   # and
ASSIGN  = "assign"        # =
DECLARE = "declare"       # :=
COMMA   = "comma"         # ,
ARROW   = "arrow"         # ->

# Keywords
DEF    = "def"
RETURN = "return"
TRUE   = "true"  
FALSE  = "false"
NULL   = "null"
IF     = "if"
ELSE   = "else"
ELIF   = "elif"

class Token(object):
    """a single lexical token"""
    def __init__(self, t, literal, start = (0, 0), end = (0, 0)):
        self.type = t          # "type"
        self.literal = literal # "literal"
        self.start = start     # (line, col)
        self.end = end         # (line, col)
    
    def __str__(self):
        return "%s '%s' from %s:%s to %s:%s" % (
            self.type, self.literal,
            self.start[0], self.start[1],
            self.end[0], self.end[1]
        )
        
    def __repr__(self):
        return self.__str__()
        
keywords = {
    "def":    DEF,
    "return": RETURN,
    "true":   TRUE,
    "yes":    TRUE,
    "false":  FALSE,
    "no":     FALSE,
    "null":   NULL,
    "if":     IF,
    "else":   ELSE,
    "elif":   ELIF
}
        