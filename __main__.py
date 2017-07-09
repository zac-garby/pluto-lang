#!/usr/bin/env python3

import token
import lexer as l
import parser as p

def main():
    string = input(">> ")
    string = string.replace("\\n", "\n") + ";"
            
    tokens = l.lex(string)
    
    parser = p.Parser(tokens)
    program = parser.parse_program()
    
    if len(parser.errors) > 0:
        parser.print_errors()
    else:
        print(program)
    
if __name__ == "__main__":
    while True:
        try:
            main()
        except (KeyboardInterrupt, EOFError):
            print('Goodbye!')
            break
            