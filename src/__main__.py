#!/usr/bin/env python3

import sys
import readline
import argparse

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
    parser.add_argument("-v", "--version", action="version", version="Pluto v1.0  --  Copyright Zac Garby © 2017")

    args = parser.parse_args()

    if args.file == None:
        repl(c.Context())
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
            execute(text, False, ctx)

            if args.interactive:
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

        if (print_result and type(result) != o.Null) or type(result) == o.Error:
            print(result)

def repl(ctx):
    print("Welcome to Pluto's REPL!")
    print("""
                   .....
               ``..--:/+oo/-
            ``    ``.-:/+osys-
          ...``````.--:/+osyhh+
         -/::-----::ooosssyymmm=
         oo+++////++oossyyhddmmh
         yyyyssssssyyyhhdddmmmNd
         odddddhhddddddmmmmNNNN+
         `ymmmmmmmmmmNNNNNNNNMs
          `+mNNNNNNNNNNNMMMMm/
            `+hNMMMMMMMMMNy/`
               `-/+ooo+/.
    """)
    while True:
        try:
            string = input("⧫ ") + ";"

            if string[:-1] == "exit":
                break

            execute(string, True, ctx)
        except (KeyboardInterrupt, EOFError):
            break

def run_file():
    with open(sys.argv[1], "r") as f:
        content = f.read()
        execute(content, False, c.Context())

if __name__ == "__main__":
    main()

