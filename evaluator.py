import object as obj
import ast

NULL = obj.Null()
TRUE = obj.Boolean(True)
FALSE = obj.Boolean(False)

def eval(node, ctx):    
    t = type(node)
    
    # Constructs
    if t == ast.Program:              return eval_program(node, ctx)
    if t == ast.BlockStatement:       return eval_block_stmt(node, ctx)
    if t == ast.ExpressionStatement:  return eval(node.expr, ctx)
    if t == ast.IfExpression:         return eval_if(node, ctx)
    
    # Literals
    if t == ast.Null:                 return NULL
    if t == ast.Number:               return obj.Number(node.value)
    if t == ast.String:               return obj.String(node.value)
    if t == ast.Boolean:              return bool_obj(node.value)
    if t == ast.Identifier:           return eval_id(node, ctx)
    
    if t == ast.Array:
        elements = eval_exprs(node.elements, ctx)
        
        if len(elements) == 1 and is_err(elements[0]):
            return elements[0]
        
        return obj.Array(elements)
    
    # More complex nodes
    if t == ast.ReturnStatement:
        val = eval(node.value, ctx)
        return val if is_err(val) else obj.ReturnValue(val)
        
    if t == ast.PrefixExpression:
        right = eval(node.right, ctx)
        return right if is_err(right) else eval_prefix(node.operator, right)
        
    if t == ast.InfixExpression:
        left = eval(node.left, ctx)
        if is_err(left): return left
        
        right = eval(node.right, ctx)
        if is_err(right): return right
        
        return eval_infix(node.operator, left, right, ctx)
        
    if t == ast.AssignExpression:
        right = eval(node.value, ctx)
        return right if is_err(right) else eval_assign(node.name, right, ctx)
        
    return err("evaluation for %s not yet implemented" % t)
    
err = obj.Error

def is_err(o):
    return False if o == None else o.type == obj.ERROR
    
def eval_exprs(exprs, ctx):
    result = []
    
    for expr in exprs:
        o = eval(expr, ctx)
        
        if is_err(o):
            return [o]
            
        result.append(o)
        
    return result
    
def eval_program(program, ctx):
    if len(program.statements) == 0:
        return NULL
        
    result = None
    
    for stmt in program.statements:
        result = eval(stmt, ctx)
        
        if is_err(result):
            return result
        
        if result.type == obj.RETURN_VALUE:
            return result.value
        
    return result
    
def eval_block_stmt(block, ctx):
    if len(block.statements) == 0:
        return NULL
        
    result = None
    
    for stmt in block.statements:
        result = eval(stmt, ctx)
        
        if result != None:
            t = result.type
            
            if t == obj.RETURN_VALUE or t == obj.ERROR:
                return result
                
    return result
    
def eval_id(node, ctx):
    val = ctx[node.value]
    
    if val != None:
        return val
        
    return err("%s is not defined in the current context" % node.value)
    
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
    
def eval_infix(op, left, right, ctx):
    # Boolean operators
    if op == "&&": return bool_obj(is_truthy(left) and is_truthy(right))
    if op == "||": return bool_obj(is_truthy(left) or is_truthy(right))
    if op == "==": return bool_obj(left == right)
    if op == "!=": return bool_obj(left != right)
    
    if left.type == obj.NUMBER and right.type == obj.NUMBER:
        return eval_number_infix(op, left, right)
        
    if left.type == obj.STRING and right.type == obj.STRING:
        return eval_string_infix(op, left, right)
        
    return err("unknown operator: %s %s %s" % (left.type, op, right.type))
    
def eval_number_infix(op, left, right):
    l = left.value
    r = right.value
    
    if op == "+": return obj.Number(l + r)
    if op == "-": return obj.Number(l - r)
    if op == "*": return obj.Number(l * r)
    if op == "/": return obj.Number(l / r)
    if op == "<": return bool_obj(l < r)
    if op == ">": return bool_obj(l > r)
    if op == "&": return float(int(l) & int(r))
    if op == "|": return float(int(l) | int(r))
    
    return err("unknown operator: %s %s %s" % (left.type, op, right.type))
    
def eval_string_infix(op, left, right):
    if op == "+": return obj.String(left.value + right.value)
    
    return err("unknown operator: %s %s %s" % (left.type, op, right.type))
    
def eval_if(expr, ctx):
    condition = eval(expr.condition, ctx)
    
    if is_err(condition): return condition
    
    if is_truthy(condition):
        return eval(expr.consequence, ctx)
    elif expr.alternative != None:
        return eval(expr.alternative, ctx)
    else:
        return NULL
        
def is_truthy(o):
    return not (o == NULL or o == FALSE)
    
def bool_obj(o):
    return TRUE if o else FALSE