import obj
import ast
import math
import types

NULL  = obj.Null()
TRUE  = obj.Boolean(True)
FALSE = obj.Boolean(False)

NEXT  = obj.Next()
BREAK = obj.Break()

overloadable_infixes = {
    "+":  "__plus $",
    "-":  "__minus $",
    "*":  "__times $",
    "/":  "__divide $",
    "**": "__exp $",
    "//": "__f_div $",
    "%":  "__mod $",
    "==": "__eq $",
    "||": "__or $",
    "&&": "__and $",
    "|":  "__b_or $",
    "&":  "__b_and $",
    ".":  "__get $"
}

overloadable_prefixes = {
    "+": "__no_op",
    "-": "__negate"
}

def evaluate(node, ctx):
    t = type(node)

    # Constructs
    if t == ast.Program:              return eval_program(node, ctx)
    if t == ast.BlockStatement:       return eval_block_stmt(node, ctx)
    if t == ast.ExpressionStatement:  return evaluate(node.expr, ctx)
    if t == ast.IfExpression:         return eval_if(node, ctx)
    if t == ast.WhileLoop:            return eval_while_loop(node, ctx)
    if t == ast.ForLoop:              return eval_for_loop(node, ctx)
    if t == ast.ClassStatement:       return eval_class_stmt(node, ctx)
    if t == ast.MethodCall:           return eval_method_call(node, ctx)
    if t == ast.MatchExpression:      return eval_match_expr(node, ctx)
    if t == ast.TryExpression:        return eval_try_expr(node, ctx)

    # Literals
    if t == ast.Null:                 return NULL
    if t == ast.Number:               return obj.Number(node.value)
    if t == ast.String:               return obj.String(node.value)
    if t == ast.Char:                 return obj.Char(node.value)
    if t == ast.Boolean:              return bool_obj(node.value)
    if t == ast.Identifier:           return eval_id(node, ctx)
    if t == ast.BlockLiteral:         return eval_block(node, ctx)

    if t == ast.NextStatement:        return NEXT
    if t == ast.BreakStatement:       return BREAK

    # Functions
    if t == ast.FunctionDefinition:   return eval_function_def(node, ctx)
    if t == ast.InitDefinition:       return eval_init_def(node, ctx)
    if t == ast.FunctionCall:         return eval_function_call(node, ctx)

    if t == ast.Array:
        elements = eval_exprs(node.elements, ctx)

        if len(elements) == 1 and is_err(elements[0]):
            return elements[0]

        return obj.Array(elements)

    if t == ast.Map:
        keys = eval_exprs(node.pairs.keys(), ctx)
        if len(keys) == 1 and is_err(keys[0]):
            return keys[0]

        values = eval_exprs(node.pairs.values(), ctx)
        if len(values) == 1 and is_err(values[0]):
            return values[0]

        return obj.Map(list(zip(keys, values)))

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
        return right if is_err(right) else eval_prefix(ctx, node.operator, right)

    if t == ast.InfixExpression:
        left = evaluate(node.left, ctx)
        if is_err(left): return left

        right = evaluate(node.right, ctx)
        if is_err(right): return right

        return eval_infix(node.operator, left, right, ctx)

    if t == ast.AssignExpression:
        right = evaluate(node.value, ctx)
        if is_err(right): return right
        
        if type(node.name) == ast.DotExpression:
            o = evaluate(node.name.left, ctx)
            
            if type(node.name.right) == ast.Identifier:
                o[node.name.right.value] = right
                return right
            else:
                return err(ctx, "an identifier is expected to follow a dot operator", "SyntaxError")
        
        return eval_assign(node.name, right, ctx)

    if t == ast.DeclareExpression:
        right = evaluate(node.value, ctx)
        return right if is_err(right) else eval_declare(node.name, right, ctx)
        
    if t == ast.DotExpression:
        left = evaluate(node.left, ctx)
        if is_err(left): return left
        
        if type(node.right) == ast.Identifier:
            try:
                return left[node.right.value]
            except:
                return err(ctx, "cannot access fields of %s" % left.type, "TypeError")
        
        return err(ctx, "an identifier is expected to follow a dot operator", "SyntaxError")

    return err(ctx, "evaluation for %s not yet implemented" % t, "NotImplementedError")

def err(ctx, msg, tag):
    e = obj.Instance(ctx["Error"])
    if e.base == None:
        print("Since the prelude isn't loaded, errors cannot be thrown!")
        return NULL
    
    e["tag"] = obj.String(tag)
    e["msg"] = obj.String(msg)
    
    return e

def is_err(o):
    return False if o == None else type(o) == obj.Instance and o.base.name == "Error"

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

        if is_err(result) or result != None and result.type in [obj.RETURN_VALUE, obj.NEXT, obj.BREAK]:
            return result

    return result

def eval_id(node, ctx):
    val = ctx[node.value]

    if val != None:
        return val

    return err(ctx, "`%s` is not defined in the current context" % node.value, "NotFoundError")

def eval_prefix(op, right, ctx):
    if op == "-": return eval_minus_prefix(right)
    if op == "+": return right
    return err(ctx, "unknown operator: %s%s", op, right.type, "NotFoundError")

def eval_minus_prefix(right, ctx):
    if right.type != obj.NUMBER: return err(ctx, "unknown operator: -%s" % right.type, "NotFoundError")
    return obj.Number(-right.value)

def eval_assign(left, right, ctx):
    if type(left) != ast.Identifier:
        return err(ctx, "cannot assign to %s, expected an identifier" % type(left), "SyntaxError")

    ctx[left.value] = right

    return right

def eval_declare(left, right, ctx):
    if type(left) != ast.Identifier:
        return err(ctx, "cannot assign to %s, expected an identifier" % type(left), "SyntaxError")

    ctx.store[left.value] = right

    return right

def eval_infix(op, left, right, ctx):
    if isinstance(left, obj.Collection) and isinstance(right, obj.Collection):
        return eval_collection_infix(op, left, right, ctx)
        
    if isinstance(left, obj.Instance):
        return eval_instance_infix(op, left, right, ctx)

    # Boolean operators
    if op == "&&": return bool_obj(is_truthy(left) and is_truthy(right))
    if op == "||": return bool_obj(is_truthy(left) or is_truthy(right))
    if op == "==": return bool_obj(left == right)
    if op == "!=": return bool_obj(left != right)

    if op == "?":
        return right if left == NULL else left

    if type(left) == obj.Number and type(right) == obj.Number:
        return eval_number_infix(op, left, right, ctx)

    if (type(left) == obj.Char and type(right) == obj.Char or
       type(left) == obj.String and type(right) == obj.Char or
       type(left) == obj.Char and type(right) == obj.String):
        return eval_char_string_infix(op, left, right, ctx)

    if (type(left) == obj.Char and type(right) == obj.Number):
        return obj.String(left.value * math.floor(right.value))

    if isinstance(left, obj.Collection) and type(right) == obj.Number and op == "*":
        result = []
        elems = left.get_elements()
        n = math.floor(right.value)

        for _ in range(n):
            result += elems[:]

        return type(left)(result)

    return err(ctx, "unknown operator: %s %s %s" % (left.type, op, right.type), "NotFoundError")

def eval_instance_infix(op, left, right, ctx):
    fn_name = overloadable_infixes[op]
    fn_pattern = fn_name.split()
    
    for method in left.base.get_methods():
        method_pattern = method.fn.pattern
        
        if len(fn_pattern) != len(method_pattern):
            continue
        
        is_match = True
        for i in range(len(method_pattern)):
            if not (fn_pattern[i] == "$" and type(method_pattern[i]) == ast.Parameter or
                    type(method_pattern[i]) == ast.Identifier and fn_pattern[i] == method_pattern[i].value):
                is_match = False
        
        if is_match:
            args = {}
            
            for i in range(len(method_pattern)):
                item = method_pattern[i]
                f_item = fn_pattern[i]

                if type(item) == ast.Parameter:
                    args[item.name] = right
            
            args["self"] = left
    
            enclosed = ctx.enclose_with_args(args)
    
            return evaluate(method.fn.body, enclosed)
    
    return err(ctx, "unknown operator: %s %s %s" % (left.base, op, right.type), "NotFoundError")

def eval_char_string_infix(op, left, right, ctx):
    l = left.value
    r = right.value

    if op == "+": return obj.String(l + r)
    if op == "-": return obj.String([ch for ch in l if ch != r])

    return err(ctx, "unknown operator: %s %s %s" % (left.type, op, right.type), "NotFoundError")

def eval_number_infix(op, left, right, ctx):
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

    return err(ctx, "unknown operator: %s %s %s" % (left.type, op, right.type), "NotFoundError")

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

    return err(ctx, "unknown operator: %s %s %s" % (left.type, op, right.type), "NotFoundError")

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
        return err(ctx, "no function matching the pattern: %s" % p_string, "NotFoundError")

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
        
        on_call_result = function.on_call(args, ctx, enclosed)

        if on_call_result != None or is_err(on_call_result):
            return on_call_result

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
        return err(ctx, "cannot use a for loop over a collection of type %s" % collection.type, "TypeError")

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

def eval_class_stmt(node, ctx):
    o = obj.Class(node.name.value, None, [])
    
    if node.parent != None:
        o.parent = evaluate(node.parent, ctx)
        if is_err(o.parent):
            return o.parent
    
    for mnode in node.methods:
        fn = obj.Function(mnode.pattern, mnode.body, ctx)
        method = None

        if type(mnode) == ast.FunctionDefinition:
            method = obj.Method(fn)
        elif type(mnode) == ast.InitDefinition:
            method = obj.InitMethod(fn)
            
            init_pattern = [node.name] + fn.pattern
            
            def on_init(self, args, ctx, enclosed):
                enclosed["self"] = obj.Instance(o)
                
                result = evaluate(self.body, enclosed)
                if is_err(result):
                    return result
                
                return enclosed["self"]
            
            init_fn = obj.Function(init_pattern, mnode.body, ctx)
            init_fn.on_call = types.MethodType(on_init, init_fn)
            
            ctx.add_function(init_fn)

        o.methods.append(method)
    
    ctx[o.name] = o

    return o

def eval_method_call(node, ctx):
    instance = evaluate(node.instance, ctx)
    if is_err(instance):
        return instance
    
    pattern = node.pattern
    function = None
    
    for func in instance.base.get_methods():
        if len(pattern) != len(func.fn.pattern):
            continue

        matched = True

        for i in range(len(pattern)):
            item = pattern[i]
            f_item = func.fn.pattern[i]

            if type(item) == ast.Identifier and type(f_item) == ast.Identifier:
                if item.value != f_item.value:
                    matched = False
            elif not(type(item) == ast.Argument and type(f_item) == ast.Parameter):
                matched = False

        if matched:
            function = func
            break
    
    if function == None:
        p_string = "".join((e.value if type(e) == ast.Identifier else "$") + " " for e in node.pattern)[:-1]
        return err(ctx, "could not find a method of %s matching the pattern '%s'" % (instance.base.name, p_string), "NotFoundError")
    
    args = {}
    
    for i in range(len(node.pattern)):
        item = node.pattern[i]
        f_item = function.fn.pattern[i]

        if type(item) == ast.Argument and type(f_item) == ast.Parameter:
            evaled = evaluate(item.value, ctx)
            if is_err(evaled):
                return evaled

            args[f_item.name] = evaled
            
    args["self"] = instance
    
    enclosed = ctx.enclose_with_args(args)
    
    return evaluate(function.fn.body, enclosed)

def eval_match_expr(node, ctx):
    val = evaluate(node.expr, ctx)
    if is_err(val):
        return val
    
    matched = None
    
    for exprs, result in node.arms:  
        m = False
              
        if exprs == None:
            m = True
        else:
            for expr in exprs:
                e = evaluate(expr, ctx)
                if is_err(e):
                    return e
            
                if e == val:
                    m = True
        
        if m:
            matched = result
            break
    
    if matched != None:
        r = evaluate(matched, ctx.enclose())
        return unwrap_return_value(r)
    else:
        return NULL

def eval_try_expr(node, ctx):
    val = evaluate(node.body, ctx)
    
    if not (val.type == obj.INSTANCE and val.base.name == "Error"):
        return val
    
    matched = None
    
    for exprs, result in node.arms:
        m = False
        
        if not exprs:
            m = True
        else:
            for expr in exprs:
                e = evaluate(expr, ctx)
                if is_err(e):
                    return e
            
                if e.type != obj.STRING:
                    return err(ctx, 
                        "All catch-arm predicate values must be strings. Found a %s" % e.type,
                        "TypeError"
                    )
                
                if e == val["tag"]:
                    m = True
        
        if m:
            matched = result
            break
    
    if matched != None:        
        err_obj = obj.Map([
            (obj.String("tag"), val["tag"]),
            (obj.String("msg"), val["msg"])
        ])
        
        enclosed = ctx.enclose_with_args({
            node.err_name.value: err_obj
        })

        r = evaluate(matched, enclosed)
        return unwrap_return_value(r)
    else:
        return val

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
