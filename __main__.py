#!/usr/bin/env python3

import token
import lexer as l
import parser as p
import evaluator as e
import context as c

def main(ctx):
    string = input(">> ")
    string = string.replace("\\n", "\n") + ";"
            
    tokens = l.lex(string)
    
    parser = p.Parser(tokens)
    program = parser.parse_program()
    
    if len(parser.errors) > 0:
        parser.print_errors()
    else:
        # print(program)
        print(e.eval(program, ctx))
    
if __name__ == "__main__":
    ctx = c.Context()
    
    while True:
        try:
            main(ctx)
        except (KeyboardInterrupt, EOFError):
            print('Goodbye!')
            break
            