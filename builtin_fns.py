import object as obj
import ast
import context
from evaluator import NULL, TRUE, FALSE, evaluate, err


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
            if args[name].type != expected_type:
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
        
@arg("block", obj.BLOCK)
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
    
@arg("block", obj.BLOCK)
@arg("args", obj.ARRAY)
@builtin("run $block with $args")
def run_block_with_args(args, context):
    block = args["block"]
    b_args = args["args"]
    
    if len(block.params) != len(b_args.elements):
        return err("the amount of arguments provided in 'run $block with $args' should match the number of parameters in the block")
    
    params = [param.value for param in block.params]
    args_dictionary = dict(zip(params, b_args.elements))
    
    ctx = context.enclose_with_args(args_dictionary)
    return evaluate(block.body, ctx)
    
@arg("block", obj.BLOCK)
@arg("array", obj.ARRAY)
@builtin("map $block over $array")
def map_block_over_array(args, context):
    array = args["array"].elements
    block = args["block"]
    
    result = []
    
    for item in array:
        mapped = _run_block(block, [item], context)
        
        if mapped.type == obj.ERROR:
            return mapped
            
        result.append(mapped)
        
    return obj.Array(result)

@arg("array", obj.ARRAY)
@arg("block", obj.BLOCK)
@builtin("left fold $array with $block")
@builtin("fold $array with $block")
def fold_array_with_block(args, context):
    array = args["array"].elements
    block = args["block"]
    
    result = array[0]
    
    for item in array[1:]:
        mapped = _run_block(block, [result, item], context)
        
        if mapped.type == obj.ERROR:
            return mapped
            
        result = mapped
        
    return result

@arg("array", obj.ARRAY)
@arg("block", obj.BLOCK)
@builtin("right fold $array with $block")
def fold_array_with_block(args, context):
    array = args["array"].elements
    array.reverse()
    
    block = args["block"]
    
    result = array[0]
    
    for item in array[1:]:
        mapped = _run_block(block, [result, item], context)
        
        if mapped.type == obj.ERROR:
            return mapped
            
        result = mapped
        
    return result
    
@arg("array", obj.ARRAY)
@builtin("append $item to $array")
def append_item_to_array(args, context):
    item = args["item"]
    array = args["array"]
    
    array.elements.append(item)
    
    return array
    
@arg("i", obj.NUMBER)
@arg("array", obj.ARRAY)
@builtin("index $i of $array")
def index_i_of_array(args, context):
    i = args["i"]
    array = args["array"]
    
    if not i.is_integer() or not i.is_positive() or not int(i.value) < len(array.elements):
        return err("invalid index: %s" % i)
        
    return array.elements[int(i.value)]
    
@arg("start", obj.NUMBER)
@arg("end", obj.NUMBER)
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