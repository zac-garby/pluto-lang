#!/usr/bin/env python3

import token
import lexer
import parser

def main():
    string = input(">> ")
    string = string.replace("\\n", "\n") + ";"
            
    tokens = lexer.lex(string)
    p = parser.Parser(tokens)
    program = p.parse_program()
    print(program)
    
if __name__ == "__main__":
    while True:
        try:
            main()
        except (KeyboardInterrupt, EOFError):
            print('Goodbye!')
            break
            