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
    
    print(program)
    print(parser.errors)
    
if __name__ == "__main__":
    while True:
        try:
            main()
        except (KeyboardInterrupt, EOFError):
            print('Goodbye!')
            break
            