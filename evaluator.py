import obj
import ast

NULL  = obj.Null()
TRUE  = obj.Boolean(True)
FALSE = obj.Boolean(False)

NEXT  = obj.Next()
BREAK = obj.Break()

def evaluate(node, ctx):
    t = type(node)
    
    # Constructs
    if t == ast.Program:              return eval_program(node, ctx)
    if t == ast.BlockStatement:       return eval_block_stmt(node, ctx)
    if t == ast.ExpressionStatement:  return evaluate(node.expr, ctx)
    if t == ast.IfExpression:         return eval_if(node, ctx)
    if t == ast.WhileLoop:            return eval_while_loop(node, ctx)
    if t == ast.ForLoop:              return eval_for_loop(node, ctx)
    
    # Literals
    if t == ast.Null:                 return NULL
    if t == ast.Number:               return obj.Number(node.value)
    if t == ast.String:               return obj.String(node.value)
    if t == ast.Boolean:              return bool_obj(node.value)
    if t == ast.Identifier:           return eval_id(node, ctx)
    if t == ast.BlockLiteral:         return eval_block(node, ctx)
    
    if t == ast.NextStatement:        return NEXT
    if t == ast.BreakStatement:       return BREAK
    
    # Functions
    if t == ast.FunctionDefinition:   return eval_function_def(node, ctx)
    if t == ast.FunctionCall:         return eval_function_call(node, ctx)
    
    if t == ast.Array:
        elements = eval_exprs(node.elements, ctx)
        
        if len(elements) == 1 and is_err(elements[0]):
            return elements[0]
        
        return obj.Array(elements)
        
    if t == ast.Tuple:
        elements = eval_exprs(node.value, ctx)
        
        if len(elements) == 1 and is_err(elements[0]):
            return elements[0]
            
        return obj.Tuple(elements)
    
    # More complex nodes
    if t == ast.ReturnStatement:
        if node.value == None:
            return obj.ReturnValue(NULL)
        
        val = evaluate(node.value, ctx)
        return val if is_err(val) else obj.ReturnValue(val)
    
    if t == ast.PrefixExpression:
        right = evaluate(node.right, ctx)
        return right if is_err(right) else eval_prefix(node.operator, right)
    
    if t == ast.InfixExpression:
        left = evaluate(node.left, ctx)
        if is_err(left): return left
        
        right = evaluate(node.right, ctx)
        if is_err(right): return right
        
        return eval_infix(node.operator, left, right, ctx)
    
    if t == ast.AssignExpression:
        right = evaluate(node.value, ctx)
        return right if is_err(right) else eval_assign(node.name, right, ctx)
        
    if t == ast.DeclareExpression:
        right = evaluate(node.value, ctx)
        return right if is_err(right) else eval_declare(node.name, right, ctx)
    
    return err("evaluation for %s not yet implemented" % t)

err = obj.Error

def is_err(o):
    return False if o == None else type(o) == obj.Error

def eval_exprs(exprs, ctx):
    result = []
    
    for expr in exprs:
        o = evaluate(expr, ctx)
        
        if is_err(o):
            return [o]
        
        result.append(o)
    
    return result

def eval_program(program, ctx):
    if len(program.statements) == 0:
        return NULL
    
    result = None
    
    for stmt in program.statements:
        result = evaluate(stmt, ctx)
        
        if is_err(result):
            return result
        
        if type(result) == obj.ReturnValue:
            return result.value
            
        if type(result) in [obj.Next, obj.Break]:
            return NULL
    
    return result

def eval_block_stmt(block, ctx):
    if len(block.statements) == 0:
        return NULL
    
    result = None
    
    for stmt in block.statements:
        result = evaluate(stmt, ctx)
        
        if result != None:
            t = result.type
            
            if t in [obj.RETURN_VALUE, obj.ERROR, obj.NEXT, obj.BREAK]:
                return result
    
    return result

def eval_id(node, ctx):
    val = ctx[node.value]
    
    if val != None:
        return val
    
    return err("'%s' is not defined in the current context" % node.value)

def eval_prefix(op, right):
    if op == "-": return eval_minus_prefix(right)
    if op == "+": return right
    return err("unknown operator: %s%s", op, right.type)

def eval_minus_prefix(right):
    if right.type != obj.NUMBER: return err("unknown operator: -%s" % right.type)
    return obj.Number(-right.value)

def eval_assign(left, right, ctx):
    if type(left) != ast.Identifier:
        return err("cannot assign to %s, expected an identifier", left.type)
    
    ctx[left.value] = right
    
    return right
    
def eval_declare(left, right, ctx):
    if type(left) != ast.Identifier:
        return err("cannot assign to %s, expected an identifier", left.type)
    
    ctx.store[left.value] = right
    
    return right

def eval_infix(op, left, right, ctx):
    if isinstance(left, obj.Collection) and isinstance(right, obj.Collection):
        return eval_collection_infix(op, left, right, ctx)
    
    # Boolean operators
    if op == "&&": return bool_obj(is_truthy(left) and is_truthy(right))
    if op == "||": return bool_obj(is_truthy(left) or is_truthy(right))
    if op == "==": return bool_obj(left == right)
    if op == "!=": return bool_obj(left != right)
    
    if op == "?":
        return right if left == NULL else left
    
    if type(left) == obj.Number and type(right) == obj.Number:
        return eval_number_infix(op, left, right)
    
    return err("unknown operator: %s %s %s" % (type(left), op, type(right)))

def eval_number_infix(op, left, right):
    l = left.value
    r = right.value
    
    if op == "+":  return obj.Number(l + r)
    if op == "-":  return obj.Number(l - r)
    if op == "*":  return obj.Number(l * r)
    if op == "/":  return obj.Number(l / r)
    if op == "&":  return obj.Number(int(l) & int(r))
    if op == "|":  return obj.Number(int(l) | int(r))
    if op == "**": return obj.Number(l ** r)
    if op == "//": return obj.Number(l // r)
    if op == "%":  return obj.Number(l % r)
    
    if op == "<":  return bool_obj(l < r)
    if op == ">":  return bool_obj(l > r)
    if op == "<=": return bool_obj(l <= r)
    if op == ">=": return bool_obj(l >= r)
    
    return err("unknown operator: %s %s %s" % (left.type, op, right.type))

def eval_collection_infix(op, left, right, ctx):
    l = left.get_elements()
    r = right.get_elements()
    
    if op == "==": return bool_obj(left == right)
    if op == "!=": return bool_obj(left != right)
    
    if op == "+":  return type(left)(l + r)
    if op == "-":  return type(left)([e for e in l if e not in r])
    if op in "&&": return type(left)([e for e in l if e in r])
    
    if op in "||":
        result = []
        
        for elem in l + r:
            if elem not in result:
                result.append(elem)
                
        return type(left)(result)
        
    return err("unknown operator: %s %s %s" % (type(left), op, type(right)))

def eval_if(expr, ctx):
    condition = evaluate(expr.condition, ctx)
    
    if is_err(condition): return condition
    
    if is_truthy(condition):
        return evaluate(expr.consequence, ctx)
    elif expr.alternative != None:
        return evaluate(expr.alternative, ctx)
    else:
        return NULL

def eval_function_def(node, ctx):
    function = obj.Function(node.pattern, node.body, ctx)
    ctx.add_function(function)
    
    return NULL

def eval_function_call(node, ctx):
    function = ctx.get_function(node.pattern)
    p_string = "".join((e.value if type(e) == ast.Identifier else "$") + " " for e in node.pattern)[:-1]
    
    if function == None:
        return err("no function matching the pattern: %s" % p_string)
    
    args = {}
    
    if type(function) == obj.Function:        
        for i in range(len(node.pattern)):
            item = node.pattern[i]
            f_item = function.pattern[i]
        
            if type(item) == ast.Argument and type(f_item) == ast.Parameter:
                evaled = evaluate(item.value, ctx)
                if is_err(evaled):
                    return evaled
                
                args[f_item.name] = evaled
                
        enclosed = ctx.enclose_with_args(args)
        
        result = evaluate(function.body, enclosed)
        if is_err(result):
            return result
    else:
        for i in range(len(node.pattern)):
            item = node.pattern[i]
            f_item = function.pattern[i]
            
            if type(item) == ast.Argument and f_item[0] == "$":
                evaled = evaluate(item.value, ctx)
                if is_err(evaled):
                    return evaled
                args[f_item[1:]] = evaled
        
        result = function.fn(args, ctx)
    
    if result == None:
        return NULL
    
    return unwrap_return_value(result)
    
def eval_block(node, ctx):
    return obj.Block(node.params, node.body)
    
def eval_while_loop(node, ctx):
    while True:
        condition = evaluate(node.condition, ctx)
        if is_err(condition):
            return condition
            
        if not is_truthy(condition):
            break
            
        result = evaluate(node.body, ctx.enclose())
        if is_err(result):
            return result
            
        if type(result) == obj.Break:
            break
            
    return NULL
    
def eval_for_loop(node, ctx):
    var = node.var
    body = node.body
    
    collection = evaluate(node.collection, ctx)
    if is_err(collection):
        return collection
    
    items = None
    if isinstance(collection, obj.Collection):
        items = collection.get_elements()
        
    if items == None:
        return err("cannot use a for loop over a collection of type %s" % collection.type)
        
    for item in items:
        enclosed = ctx.enclose_with_args({
            var.value: item
        })
        
        result = evaluate(body, enclosed)
        if is_err(result):
            return result
            
        if type(result) == obj.Break:
            break
    
    return NULL

def unwrap_return_value(o):
    if type(o) == obj.ReturnValue:
        return o.value
    
    return o

def is_truthy(o):
    return not (
        o == NULL or
        o == FALSE or
        type(o) == obj.Number and o.value == 0 or
        isinstance(o, obj.Collection) and len(o.get_elements()) == 0
    )

def bool_obj(o):
    return TRUE if o else FALSE