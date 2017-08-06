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


def pattern(pattern):
    def pattern_decorator(fn):
        setattr(fn, "pattern", pattern)
        return fn
    
    return pattern_decorator

def builtin(fn):
    Builtin(getattr(fn, "pattern"), fn)
    return fn

def arg(name, expected_type):
    def arg_decorator(fn):     
        def new_fn(args, context):            
            if not isinstance(args[name], expected_type):                
                return err("the $%s parameter must be of type %s, not %s" % (
                    name,
                    expected_type.t,
                    args[name].type
                ))

            return fn(args, context)
        
        return new_fn

    return arg_decorator


## Builtin definitions ##

@builtin
@pattern("round $n")
@arg("n", obj.Number)
def round_n(args, context):
    n = args["n"]
    
    return obj.Number(round(n.value))

@builtin
@pattern("print $obj")
def print_obj(args, context):
    print(args["obj"])
    return NULL

@builtin
@pattern("print $obj without newline")
def print_obj_without_newline(args, context):
    print(args["obj"], end="")
    return NULL

@builtin
@pattern("input")
def _input(args, context):
    try:
        return obj.String(input())
    except (KeyboardInterrupt, EOFError):
        return NULL

@builtin
@pattern("input with prompt $prompt")
def input_with_prompt_prompt(args, context):
    try:
        return obj.String(input(args["prompt"]))
    except (KeyboardInterrupt, EOFError):
        return NULL

def _run_block(block, args, context):
    params = [param.value for param in block.params]
    args_dict = dict(zip(params, args))
    ctx = context.enclose_with_args(args_dict)
    return evaluate(block.body, ctx)

@builtin
@pattern("do $block")
@arg("block", obj.Block)
def do_block(args, context):
    block = args["block"]

    if type(block) != obj.Block:
        return err("the $block parameter in `do $block` must be of type <block>")

    if len(block.params) > 0:
        return err("since no arguments are provided, $block of `do $block` must have no parameters")

    return _run_block(block, [], context)

@builtin
@pattern("do $block with $args")
@arg("block", obj.Block)
@arg("args", obj.Collection)
def do_block_with_args(args, context):
    block = args["block"]
    b_args = args["args"].get_elements()

    if type(block) != obj.Block:
        return err("the $block parameter in `do $block with $args` must be of type <block>")

    if len(block.params) != len(b_args):
        return err("the amount of arguments provided in `do $block with $args` should match the number of parameters in the block")

    return _run_block(block, b_args, context)

@builtin
@pattern("do $block on $arg")
@arg("block", obj.Block)
def do_block_on_arg(args, context):
    block = args["block"]
    arg = args["arg"]
    
    if type(block) != obj.Block:
        return err("the $block parameter in `do $block with $args` must be of type <block>")
    
    return _run_block(block, [arg], context)

@builtin
@pattern("map $block over $array")
@arg("block", obj.Block)
@arg("array", obj.Collection)
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

@builtin
@pattern("left fold $array with $block")
@arg("array", obj.Collection)
@arg("block", obj.Block)
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

@builtin
@pattern("left fold $array with $block from $start")
@arg("array", obj.Collection)
@arg("block", obj.Block)
def fold_array_with_block(args, context):
    array = args["array"].get_elements()
    block = args["block"]

    result = args["start"]

    if len(array) == 0:
        return result

    for item in array:
        mapped = _run_block(block, [result, item], context)

        if mapped.type == obj.ERROR:
            return mapped

        result = mapped

    return result

@builtin
@pattern("right fold $array with $block")
@arg("array", obj.Collection)
@arg("block", obj.Block)
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
    
@builtin
@pattern("right fold $array with $block from $start")
@arg("array", obj.Collection)
@arg("block", obj.Block)
def fold_array_with_block(args, context):
    array = args["array"].get_elements()
    array.reverse()

    block = args["block"]
    result = args["start"]

    for item in array:
        mapped = _run_block(block, [result, item], context)

        if mapped.type == obj.ERROR:
            return mapped

        result = mapped

    return result

@builtin
@pattern("filter $array by $predicate")
@arg("array", obj.Collection)
@arg("predicate", obj.Block)
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

@builtin
@pattern("union of $a and $b")
@arg("a", obj.Collection)
@arg("b", obj.Collection)
def union_of_a_and_b(args, context):
    a = args["a"].get_elements()
    b = args["b"].get_elements()

    result = []

    for item in a + b:
        if item not in result:
            result.append(item)

    return type(args["a"])(result)

@builtin
@pattern("intersection of $a and $b")
@arg("a", obj.Collection)
@arg("b", obj.Collection)
def union_of_a_and_b(args, context):
    a = args["a"].get_elements()
    b = args["b"].get_elements()

    result = [elem for elem in a if elem in b]

    return type(args["a"])(result)

@builtin
@pattern("index $i of $array")
@arg("i", obj.Number)
@arg("array", obj.Collection)
def index_i_of_array(args, context):
    i = args["i"]
    array = args["array"]

    if not i.is_integer() or not i.is_positive() or not int(i.value) < len(array.get_elements()):
        return err("invalid index: %s" % i)

    return array.get_elements()[int(i.value)]

@builtin
@pattern("key $key of $obj")
@arg("obj", obj.Object)
def key_of_obj(args, context):
    key = args["key"]
    obj = args["obj"]

    if key not in obj.pairs.keys():
        return err("key %s not found" % key)

    return obj.pairs[key]

@builtin
@pattern("keys of $obj")
@arg("obj", obj.Object)
def keys_of_obj(args, context):
    return obj.Array(args["obj"].pairs.keys())

@builtin
@pattern("values of $obj")
@arg("obj", obj.Object)
def values_of_obj(args, context):
    return obj.Array(args["obj"].pairs.values())

@builtin
@pattern("pairs of $obj")
@arg("obj", obj.Object)
def pairs_of_obj(args, context):
    o = args["obj"]
    pairs = []

    for (key, value) in o.pairs.items():
        pairs.append(obj.Tuple([key, value]))

    return obj.Array(pairs)

@builtin
@pattern("$start to $end")
@arg("start", obj.Number)
@arg("end", obj.Number)
def start_to_end(args, context):
    start = args["start"]
    end = args["end"]

    if not start.is_integer():
        return err("$start in `$start to $end` must be an integer")

    if not end.is_integer():
        return err("$end in `$start to $end` must be an integer")

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

@builtin
@pattern("format $format with $args")
@arg("format", obj.String)
@arg("args", obj.Collection)
def format_string_with_args(args, context):
    fmt = args["format"].value
    items = tuple(args["args"].get_elements())

    try:
        return obj.String(fmt % items)
    except TypeError:
        return err("Wrong number of arguments to format `%s`" % fmt)

@builtin
@pattern("printf $format with $args")
@arg("format", obj.String)
@arg("args", obj.Collection)
def printf_format_with_args(args, context):
    fmt = args["format"].value
    items = tuple(args["args"].get_elements())

    try:
        print(obj.String(fmt % items))
    except TypeError:
        return err("Wrong number of arguments to format `%s`" % fmt)

    return NULL

