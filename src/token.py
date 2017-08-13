# etc...
EOF     = "EOF"
ILLEGAL = "illegal"

# Literals
NUM    = "number"
STR    = "string"
CHAR   = "char"
ID     = "identifier"
PARAM  = "param"

# Punctuation                     # lexeme
PLUS    = "plus"                  # +
MINUS   = "minus"                 # -
STAR    = "star"                  # *
EXP     = "exponent"              # **
SLASH   = "slash"                 # /
F_DIV   = "floor-div"             # //
MOD     = "modulo"                # %
BSLASH  = "backslash"             # \
LPAREN  = "lparen"                # (
RPAREN  = "rparen"                # )
LT      = "less-than"             # <
GT      = "greater-than"          # >
LTE     = "less-than-or-equal"    # <=
GTE     = "greater-than-or-equal" # >=
LBRACE  = "lbrace"                # {
RBRACE  = "rbrace"                # }
LSQUARE = "lsquare"               # [
RSQUARE = "rsquare"               # ]
SEMI    = "semi"                  # ;
EQ      = "equal"                 # ==
N_EQ    = "not-equal"             # !=
OR      = "or"                    # ||
AND     = "and"                   # &&
B_OR    = "bitwise-or"            # |
B_AND   = "bitwise-and"           # &
ASSIGN  = "assign"                # =
DECLARE = "declare"               # :=
COMMA   = "comma"                 # ,
ARROW   = "arrow"                 # ->
COLON   = "colon"                 # :
Q_MARK  = "question-mark"         # ?
DOT     = "dot"                   # .
F_ARROW = "fat-arrow"             # =>
BANG    = "bang"                  # !

# Keywords
DEF     = "def"
RETURN  = "return"
TRUE    = "true"
FALSE   = "false"
NULL    = "null"
IF      = "if"
ELSE    = "else"
ELIF    = "elif"
WHILE   = "while"
FOR     = "for"
NEXT    = "next"
BREAK   = "break"
CLASS   = "class"
EXTENDS = "extends"
INIT    = "init"
MATCH   = "match"
TRY     = "try"
CATCH   = "catch"

class Token(object):
    """a single lexical token"""
    def __init__(self, t, literal, start = (0, 0), end = (0, 0)):
        self.type = t          # "type"
        self.literal = literal # "literal"
        self.start = start     # (line, col)
        self.end = end         # (line, col)

    def __str__(self):
        return "%s `%s` from %s:%s to %s:%s" % (
            self.type, self.literal,
            self.start[0], self.start[1],
            self.end[0], self.end[1]
        )

    def __repr__(self):
        return self.__str__()

keywords = {
    "def":     DEF,
    "return":  RETURN,
    "true":    TRUE,
    "yes":     TRUE,
    "false":   FALSE,
    "no":      FALSE,
    "null":    NULL,
    "if":      IF,
    "else":    ELSE,
    "elif":    ELIF,
    "while":   WHILE,
    "for":     FOR,
    "next":    NEXT,
    "break":   BREAK,
    "class":   CLASS,
    "extends": EXTENDS,
    "init":    INIT,
    "match":   MATCH,
    "try":     TRY,
    "catch":   CATCH
}

