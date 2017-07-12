import math

import obj
import ast
import context
from evaluator import NULL, TRUE, FALSE, evaluate, err, is_truthy


class Builtin(object):
    builtins = []
    
    """a builtin function"""
    def __init__(self, pattern, fn):
        self.pattern = pattern.split() # e.g. ["print", "$obj"]
        self.fn = fn                   # fn(args, context) where args is a dictionary
        
        Builtin.builtins.append(self)


def builtin(pattern):    
    def builtin_decorator(fn):
        Builtin(pattern, fn)
        setattr(fn, "pattern", pattern)
        return fn
        
    return builtin_decorator
    
def arg(name, expected_type):
    def arg_decorator(fn):
        def new_fn(args, context):
            if isinstance(args[name].type, expected_type):
                return err("the $%s parameter in '%s' must be of type %s, not %s" % (
                    name,
                    getattr(fn, "pattern"),
                    expected_type,
                    args[name].type
                ))
            
            return fn(args, context)
        
        return new_fn
            
    return arg_decorator
            
    
## Builtin definitions ##  

@builtin("print $obj")
def print_obj(args, context):
    print(args["obj"])
    return NULL
    
@builtin("print $obj without newline")
def print_obj_without_newline(args, context):
    print(args["obj"], end="")
    return NULL
    
@builtin("input")
def _input(args, context):
    try:
        return obj.String(input())
    except (KeyboardInterrupt, EOFError):
        return NULL
        
@builtin("input with prompt $prompt")
def input_with_prompt_prompt(args, context):
    try:
        return obj.String(input(args["prompt"]))
    except (KeyboardInterrupt, EOFError):
        return NULL
        
@arg("block", obj.Block)
@builtin("run $block")
def run_block(args, context):
    block = args["block"]
    
    if type(block) != obj.Block:
        return err("the $block parameter in 'run $block' must be of type <block>")
    
    if len(block.params) > 0:
        return err("since no arguments are provided, $block of 'run $block' must have no parameters")
    
    ctx = context.enclose()
    return evaluate(block.body, ctx)
    
def _run_block(block, args, context):
    params = [param.value for param in block.params]
    args_dict = dict(zip(params, args))
    ctx = context.enclose_with_args(args_dict)
    return evaluate(block.body, ctx)
    
@arg("block", obj.Block)
@arg("args", obj.Collection)
@builtin("run $block with $args")
def run_block_with_args(args, context):
    block = args["block"]
    b_args = args["args"].get_elements()
    
    if len(block.params) != len(b_args):
        return err("the amount of arguments provided in 'run $block with $args' should match the number of parameters in the block")
    
    params = [param.value for param in block.params]
    args_dictionary = dict(zip(params, b_args))
    
    ctx = context.enclose_with_args(args_dictionary)
    return evaluate(block.body, ctx)
    
@arg("block", obj.Block)
@arg("array", obj.Collection)
@builtin("map $block over $array")
def map_block_over_array(args, context):
    array = args["array"].get_elements()
    block = args["block"]
    
    result = []
    
    for item in array:
        mapped = _run_block(block, [item], context)
        
        if mapped.type == obj.ERROR:
            return mapped
            
        result.append(mapped)
        
    return type(args["array"])(result)

@arg("array", obj.Collection)
@arg("block", obj.Block)
@builtin("fold $array with $block")
@builtin("left fold $array with $block")
def fold_array_with_block(args, context):
    array = args["array"].get_elements()
    block = args["block"]
    
    result = array[0]
    
    if len(array) == 0:
        return result
    
    for item in array[1:]:
        mapped = _run_block(block, [result, item], context)
        
        if mapped.type == obj.ERROR:
            return mapped
            
        result = mapped
        
    return result

@arg("array", obj.Collection)
@arg("block", obj.Block)
@builtin("right fold $array with $block")
def fold_array_with_block(args, context):
    array = args["array"].get_elements()
    array.reverse()
    
    block = args["block"]
    
    result = array[0]
    
    for item in array[1:]:
        mapped = _run_block(block, [result, item], context)
        
        if mapped.type == obj.ERROR:
            return mapped
            
        result = mapped
        
    return result
    
@arg("array", obj.Collection)
@arg("predicate", obj.Block)
@builtin("filter $array by $predicate")
def filter_array_with_predicate(args, context):
    array = args["array"].get_elements()
    predicate = args["predicate"]
    
    filtered = []
    
    for item in array:
        result = _run_block(predicate, [item], context)
        
        if result.type == obj.ERROR:
            return result
            
        if is_truthy(result):
            filtered.append(item)
            
    return type(args["array"])(filtered)
    
@arg("a", obj.Collection)
@arg("b", obj.Collection)
@builtin("union of $a and $b")
def union_of_a_and_b(args, context):
    a = args["a"].get_elements()
    b = args["b"].get_elements()
    
    result = []
    
    for item in a + b:
        if item not in result:
            result.append(item)
            
    return type(args["a"])(result)
    
@arg("a", obj.Collection)
@arg("b", obj.Collection)
@builtin("intersection of $a and $b")
def union_of_a_and_b(args, context):
    a = args["a"].get_elements()
    b = args["b"].get_elements()
    
    result = [elem for elem in a if elem in b]
    
    return type(args["a"])(result)

@arg("array", obj.Array)
@builtin("append $item to $array")
def append_item_to_array(args, context):
    item = args["item"]
    array = args["array"]
    
    array.get_elements().append(item)
    
    return array
    
@arg("i", obj.Number)
@arg("array", obj.Collection)
@builtin("index $i of $array")
def index_i_of_array(args, context):
    i = args["i"]
    array = args["array"]
    
    if not i.is_integer() or not i.is_positive() or not int(i.value) < len(array.get_elements()):
        return err("invalid index: %s" % i)
        
    return array.get_elements()[int(i.value)]
    
@arg("array", obj.Collection)
@builtin("$array contains $item")
def array_contains_item(args, context):
    return TRUE if args["item"] in args["array"].get_elements() else FALSE
    
@builtin("$obj is truthy")
def obj_is_truthy(args, context):
    return TRUE if is_truthy(args["obj"]) else FALSE
    
@arg("start", obj.Number)
@arg("end", obj.Number)
@builtin("$start to $end")
def start_to_end(args, context):
    start = args["start"]
    end = args["end"]
    
    if not start.is_integer():
        return err("$start in '$start to $end' must be an integer")
        
    if not end.is_integer():
        return err("$end in '$start to $end' must be an integer")
        
    s_val = int(start.value)
    e_val = int(end.value)
    
    if e_val < s_val:
        result = obj.Array([obj.Number(e + 1) for e in range(e_val, s_val)])
        result.elements.reverse()
        return result
    elif e_val > s_val:
        return obj.Array([obj.Number(e) for e in range(s_val, e_val)])
    else:
        return start

@arg("num", obj.Number)
@builtin("square root of $num")
def square_root_of_num(args, context):
    return obj.Number(math.sqrt(args["num"].value))
    
@arg("root", obj.Number)
@arg("num", obj.Number)
@builtin("$root st root of $num")
@builtin("$root nd root of $num")
@builtin("$root rd root of $num")
@builtin("$root th root of $num")
def nth_root_of_num(args, context):
    return obj.Number(args["num"].value ** (1 / args["root"].value))
    
@arg("format", obj.String)
@arg("args", obj.Collection)
@builtin("format $format with $args")
def format_string_with_args(args, context):
    fmt = args["format"].value
    items = tuple(args["args"].get_elements())
    
    try:
        return obj.String(fmt % items)
    except TypeError:
        return err("Wrong number of arguments to format '%s'" % fmt)
    
@arg("format", obj.String)
@arg("args", obj.Collection)
@builtin("printf $format with $args")
def printf_format_with_args(args, context):
    fmt = args["format"].value
    items = tuple(args["args"].get_elements())
    
    try:
        print(obj.String(fmt % items))
    except TypeError:
        return err("Wrong number of arguments to format '%s'" % fmt)
    
    return NULL
    
    