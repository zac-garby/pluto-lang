import object as obj
import ast
import context
from evaluator import NULL, TRUE, FALSE, evaluate, err


class Builtin(object):
    builtins = []
    
    """a builtin function"""
    def __init__(self, pattern, fn):
        self.pattern = pattern # e.g. ["print", "$obj"]
        self.fn = fn           # fn(args) where args is a dictionary
        
        Builtin.builtins.append(self)


def builtin(pattern):
    pattern = pattern.split(" ")
    
    def builtin_gen(fn):
        Builtin(pattern, fn)
        return fn
        
    return builtin_gen  
    
    
## Builtin definitions ##  

@builtin("print $obj")
def print_builtin(args, context):
    print(args["obj"])
    return NULL
    
@builtin("print $obj without newline")
def print_wn(args, context):
    print(args["obj"], end="")
    return NULL
    
@builtin("input")
def input_builtin(args, context):
    try:
        return obj.String(input())
    except (KeyboardInterrupt, EOFError):
        return NULL
        
@builtin("input with prompt $prompt")
def input_prompt_builtin(args, context):
    try:
        return obj.String(input(args["prompt"]))
    except (KeyboardInterrupt, EOFError):
        return NULL
        
@builtin("run $block")
def run_block_builtin(args, context):
    block = args["block"]
    
    if type(block) != obj.Block:
        return err("the $block parameter in 'run $block' must be of type <block>")
    
    if len(block.params) > 0:
        return err("since no arguments are provided, $block of 'run $block' must have no parameters")
    
    ctx = context.enclose()
    return evaluate(block.body, ctx)
    
@builtin("run $block with $args")
def run_block_with_args_builtin(args, context):
    block = args["block"]
    b_args = args["args"]
    
    if type(block) != obj.Block:
        return err("the $block parameter in 'run $block' must be of type <block>")
        
    if type(b_args) != obj.Array:
        return err("the $args parameter in 'run $block with $args' must be of type <array>")
    
    if len(block.params) != len(b_args.elements):
        return err("the amount of arguments provided in 'run $block with $args' should match the number of parameters in the block")
    
    params = [param.value for param in block.params]
    args_dictionary = dict(zip(params, b_args.elements))
    
    ctx = context.enclose_with_args(args_dictionary)
    return evaluate(block.body, ctx)
