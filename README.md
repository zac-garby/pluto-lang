# Pattern Based Language

![Screenshot](screenshot.png)

### What?

It's a proof-of-concept  language with a cool function definition/call syntax. Basically, instead of functions
being called with their arguments in parentheses after the name, they are represented by their patterns:

```
def this is a pattern {
  ...
};

this is a pattern;
```

This snippet defines a function with a pattern of "this is a pattern". Then, whenever a function call is
found, it searches through all the patterns which have been defined and calls the matching one. Coincidentally
this happens on the next line. It matches the pattern and calls whatever's inside the body.

Functions can, of course, also take parameters:

```
def evaluate $number times $multiplier {
  number * multiplier;
};

evaluate 5 times 10;
```

This program results in  the value `50`. Hopefully, you can see why. In  a pattern in a function  definition,
when you have a dollar sign before an identifier it means that  it's a parameter. Then, when you call it, you
place an expression inside brackets at that position. Note that, inside the  function body, you don't use the
dollar signs before the variable names. The brackets are required  to resolve any ambiguity.

Another thing -  the pattern in the above examples are  really very  verbose, so it's  probably a bad idea to
make a pattern that long, as it would take longer to type out. For vague guidelines, you might want to have a
look at the **very** tiny standard library (the four functions inside `builtin_fns.py`). A couple of them are
quite long, but they're probably less used than the others so  the longer length doesn't matter, and improves
readability significantly.

#### Other expressions as arguments

Imagine this:

```
def double $n {
  n * 2;
};

double 5 + 3;
```

What would you expect to happen? My guess would be for it to return `16`. But it doesnt - it actually returns
`13`. This is because it actually parses  the function call as `double`, then  the literal `5`, which is then
added to the other literal `3`. Essentially, it's equivalent to this:

```
(double 5) + 3;
```

So how do you avoid this? Well, since the reason it didn't work last time is because  the invisibile brackets
are in the wrong place, so you just need to tell them where to go:

```
double (5 + 3);
```

This will now give you the result you wanted.

Another problem you might come across is this:

```
def $a plus $b {
  a + b;
};
```

How would you call this? If you did the following:

```
5 plus 10;
```

You'd get an error. This is because the current grammar only allows for _implicit function calls_ if the first
item in the pattern is an identifier, and not an argument. In this case, you need to use an _explicit function call_:

```
\5 plus 10;
```

This would work exactly as you'd expect, returning the value `15`.

#### Defining your own if expression

Because of the function calling  syntax, you can actually define your  own pseudo-syntactical constructs. For
example, you could create a function which does the exact same thing as an if expression:

```
def find whether $condition is truthy of falsey and set the result to $a or $b respectively {
  if condition {
    a;
  } else {
    b;
  };
};
```

First things first: this is the first time you've seen an if expression in this language. They're fairly
standard. One main difference is that they're expressions, not statements, like in some other languages.

If expressions are also the reason the (very verbose) function defined above cannot contain the words
`if`, `else`, or `elif`.

You can then call it like this:

```
find whether true is truthy or falsey and set the result to 5 or 10 respectively;
```

Which, as you can probably guess, will return 5.

This is really cool because, in theory, you could even define the English language as a series of functions!

### How??

To use it, clone the repository and run `__main__.py`. If you  don't give in any  cmd-line arguments, it will
open up a REPL. If you give it one  argument, that should be a file name relative  to the program, which will
be run.

### Contributions

Any contributions are welcome. Just send a pull request. I'll probably accept it if it adds anything useful.

#### What can I do?

There are loads of things to do. Heres a list for you:

 - Implement loops.
 - Extend the standard library. Literally, put any function in and I'll probably accept it.
 - Extend the parser to not require semi-colons.
 - Write up some better documentation.