#!/usr/bin/env python3

import sys
import readline

import lexer      as l
import parser     as p
import evaluator  as e
import context    as c
import object     as o

def main():
    if len(sys.argv) == 1:        
        ctx = c.Context()
        
        while True:
            try:
                string = input("⧫ ") + ";"
                
                if string[:-1] == "exit":
                    break
                
                execute(string, True, ctx)
            except (KeyboardInterrupt, EOFError):
                break
        
    elif len(sys.argv) == 2:
        with open(sys.argv[1], "r") as f:
            content = f.read()
            execute(content, False, c.Context())
        
def execute(text, print_result, ctx):
    tokens = l.lex(text)
    parser = p.Parser(tokens)
    program = parser.parse_program()
        
    if len(parser.errors) > 0:
        parser.print_errors()
    else:
        result = e.evaluate(program, ctx)
        
        if (print_result and type(result) != o.Null) or type(result) == o.Error:
            print(result)
    
if __name__ == "__main__":
    main()
            