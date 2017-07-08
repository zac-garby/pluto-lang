#!/usr/bin/env python3

import token
import lexer

def main():
    string = input(">> ")
    string = string.replace("\\n", "\n")
    
    l = lexer.lex(string)
    while True:
        tok = next(l)
        print(tok)
        
        if tok.type == token.EOF:
            break
    
if __name__ == "__main__":
    while True:
        try:
            main()
        except (KeyboardInterrupt, EOFError):
            print('Goodbye!')
            break
            