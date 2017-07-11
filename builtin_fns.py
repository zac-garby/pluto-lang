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
    
    def builtin_decorator(fn):
        Builtin(pattern, fn)
        return fn
        
    return builtin_decorator
    
def arg(name, expected_type, fn_name):
    def arg_decorator(fn):
        def new_fn(args, context):
            if args[name].type != expected_type:
                return err("the $%s parameter in '%s' must be of type %s, not %s" % (
                    name,
                    fn_name,
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
        
@builtin("run $block")
@arg("block", obj.BLOCK, "run $block")
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
    
@builtin("run $block with $args")
@arg("block", obj.BLOCK, "run $block with $args")
@arg("args", obj.ARRAY, "run $block with $args")
def run_block_with_args(args, context):
    block = args["block"]
    b_args = args["args"]
    
    if len(block.params) != len(b_args.elements):
        return err("the amount of arguments provided in 'run $block with $args' should match the number of parameters in the block")
    
    params = [param.value for param in block.params]
    args_dictionary = dict(zip(params, b_args.elements))
    
    ctx = context.enclose_with_args(args_dictionary)
    return evaluate(block.body, ctx)
    
@builtin("map $block over $array")
@arg("block", obj.BLOCK, "map $block over $array")
@arg("array", obj.ARRAY, "map $block over $array")
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

@builtin("left fold $array with $block")
@builtin("fold $array with $block")
@arg("array", obj.ARRAY, "left fold $array with $block")
@arg("block", obj.BLOCK, "left fold $array with $block")
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

@builtin("right fold $array with $block")
@arg("array", obj.ARRAY, "right fold $array with $block")
@arg("block", obj.BLOCK, "right fold $array with $block")
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
    
@builtin("append $item to $array")
@arg("array", obj.ARRAY, "append $item to $array")
def append_item_to_array(args, context):
    item = args["item"]
    array = args["array"]
    
    array.elements.append(item)
    
    return array
    
@builtin("index $i of $array")
@arg("i", obj.NUMBER, "index $i of $array")
@arg("array", obj.ARRAY, "index $i of $array")
def index_i_of_array(args, context):
    i = args["i"]
    array = args["array"]
    
    if not i.is_integer() or not i.is_positive() or not int(i.value) < len(array.elements):
        return err("invalid index: %s" % i)
        
    return array.elements[int(i.value)]