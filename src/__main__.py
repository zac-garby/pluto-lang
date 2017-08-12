#!/usr/bin/env python3

import os
import sys
import argparse
import readline

import lexer      as l
import parser     as p
import evaluator  as e
import context    as c
import obj        as o

def main():
    parser = argparse.ArgumentParser(description="The interpreter for Pluto")

    parser.add_argument("-f", "--file", action="store", dest="file", type=str, help="the file to execute")
    parser.add_argument("-p", "--parse", action="store_true", default=False, help="just parse the file - don't execute it")
    parser.add_argument("-t", "--tree", action="store_true", default=False, help="print the parse tree")
    parser.add_argument("-i", "--interactive", action="store_true", default=False, help="enter interactive mode after the file has been run")
    parser.add_argument("-v", "--version", action="version", version="Pluto, early beta version")
    parser.add_argument("-n", "--no-prelude", action="store_true", dest="no_prelude", help="don't load the prelude")

    args = parser.parse_args()

    if args.file == None:
        ctx = c.Context()
        
        if not args.no_prelude:
            import_prelude(ctx)
        
        repl(ctx)
    else:
        try:
            text = open(args.file).read()

            if args.parse or args.tree:
                tokens = l.lex(text)
                parse = p.Parser(tokens)
                program = parse.parse_program()

                if len(parse.errors) > 0:
                    parse.print_errors()
                elif args.tree:
                    print(program)

                return

            ctx = c.Context()
            
            if not args.no_prelude:
                import_prelude(ctx)
            
            execute(text, False, ctx)

            if args.interactive:
                print()
                repl(ctx)

        except FileNotFoundError:
            print("File not found: %s" % args.file)
            return


def execute(text, print_result, ctx):
    tokens = l.lex(text)
    parser = p.Parser(tokens)
    program = parser.parse_program()

    if len(parser.errors) > 0:
        parser.print_errors()
    else:
        result = e.evaluate(program, ctx)

        if (print_result and type(result) != o.Null) or e.is_err(result):
            print(result)

def repl(ctx):
    print("Pluto REPL - https://pluto.zacgarby.co.uk")
    print("Copyright © Zac Garby - me@zacgarby.co.uk")

    while True:
        try:
            string = input(">> ")

            if string[:-1] == "exit":
                break

            execute(string, True, ctx)
        except (KeyboardInterrupt, EOFError):
            print("Goodbye!")
            sys.exit()

def import_prelude(ctx):
    src_path = os.path.dirname(os.path.realpath(__file__))
    prelude_path = os.path.join(src_path, "lib/prelude.pluto")
    
    with open(prelude_path, "r") as prelude:
        text = prelude.read()
        execute(text, False, ctx)

def run_file():
    with open(sys.argv[1], "r") as f:
        content = f.read()
        ctx = c.Context()
        import_prelude(ctx)
        execute(content, False, ctx)

if __name__ == "__main__":
    main()

