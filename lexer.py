import re
import token

def o(t, group = 0, transformer = (lambda t, l, w: (t, l, w))):
    return (lambda m: transformer(t, m.group(group), m.group(0)))

def id_transformer(t, l, w):
    t = token.keywords.get(l, token.ID)
    return (t, l, w)

lexical_dictionary = [
    # Literals
    (r"\d+(?:\.\d+)?",         o (token.NUM)),
    (r"\"((\\\"|[^\"])+)\"",   o (token.STR, 1)),
    (r"\w+",                   o (token.ID, 0, id_transformer)),
    (r"<([^>\n]+)>",           o (token.PARAM, 1)),
    
    # Punctuation
    (r"\+",                    o (token.PLUS)),
    (r"-",                     o (token.MINUS)),
    (r"\*",                    o (token.STAR)),
    (r"\/",                    o (token.SLASH)),
    (r"#",                     o (token.HASH)),
    (r"\(",                    o (token.LPAREN)),
    (r"\)",                    o (token.RPAREN)),
    (r"<",                     o (token.LT)),
    (r">",                     o (token.GT)),
    (r"{",                     o (token.LBRACE)),
    (r"}",                     o (token.RBRACE)),
    (r"[",                     o (token.LSQUARE)),
    (r"]",                     o (token.RSQUARE)),
    (r";",                     o (token.SEMI)),
    (r"==",                    o (token.EQ)),
    (r"!=",                    o (token.N_EQ)),
    (r"||",                    o (token.OR)),
    (r"&&",                    o (token.AND)),
    (r"|",                     o (token.B_OR)),
    (r"&",                     o (token.B_AND))
]

def lex(string, col = 1, line = 1):
    index = 0
    
    while True:        
        if index < len(string):            
            while string[index].isspace():
                index += 1
                col += 1
                
                if string[index - 1] == "\n":
                    col = 1
                    line += 1
            
            found = False
            
            for regex, handler in lexical_dictionary:
                 pattern = re.compile(regex)
                 match = pattern.match(string, index)
                 
                 if match:
                     found = True
                     t, literal, whole = handler(match)
                     yield token.Token(t, literal, (line, col), (line, col + len(whole) - 1))
                     index += len(whole)
                     col += len(whole)
                     
                     break
            
            if not found:
                yield token.Token(token.ILLEGAL, string[index], (line, col), (line, col))
                index += 1
                col += 1
        else:
            index += 1
            col += 1
            yield token.Token(token.EOF, "", (line, col), (line, col))
