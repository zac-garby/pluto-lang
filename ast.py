class Node(object):
    def literal(self):
        return self.token.literal


class Statement(Node):
    pass


class Expression(Node):
    pass


tree_indent = 2


def _(amount):
    return " " * tree_indent * amount


def n(name):
    return "" if name == "" else name + " ‣ "


def make_list_tree(indent, li, name):
    string = "%s[" % (_(indent) + n(name))

    if len(li) == 0:
        return string + "]"

    for item in li:
        string += "\n%s" % item.tree(indent + 1, "")

    return string + ("\n%s]" % _(indent))


def make_dict_tree(indent, pairs, name):
    string = "%s[" % (_(indent) + n(name))

    if len(pairs.items()) == 0:
        return string + ":]"

    for (key, value) in pairs.items():
        string += "\n%spair\n%s\n%s" % (
            _(indent + 1),
            key.tree(indent + 2, "key"),
            value.tree(indent + 2, "value")
        )

    return string + ("\n%s]" % _(indent))


class Program(object):
    """a program. contains a list of statements to be executed"""

    def __init__(self, statements):
        self.statements = statements

    def tree(self):
        return "program\n" + "".join(stmt.tree(1, "") + "\n"
                                     for stmt in self.statements)

    __str__ = tree
    __repr__ = tree


# Expressions

class Identifier(Expression):
    """an identifier node"""

    def __init__(self, token):
        self.token = token
        self.value = token.literal

    def tree(self, indent, name):
        return "%s%s" % (_(indent) + n(name), self.value)


class Number(Expression):
    """a number literal node"""

    def __init__(self, token, value):
        self.token = token
        self.value = value

    def tree(self, indent, name):
        return "%s%s" % (_(indent) + n(name), self.value)


class Boolean(Expression):
    """a boolean literal node"""

    def __init__(self, token, value):
        self.token = token
        self.value = value

    def tree(self, indent, name):
        return "%s%s" % (_(indent) + n(name), str(self.value).lower())


class String(Expression):
    """a string literal node"""

    def __init__(self, token):
        self.token = token
        self.value = token.literal

    def tree(self, indent, name):
        return '%s"%s"' % (_(indent) + n(name), self.value)


class Tuple(Expression):
    """a tuple literal node"""

    def __init__(self, token, value):
        self.token = token
        self.value = value

    def tree(self, indent, name):
        return "%stuple\n%s" % (
            _(indent) + n(name),
            make_list_tree(indent + 1, self.value, "value")
        )


class Null(Expression):
    """a null literal node"""

    def __init__(self, token):
        self.token = token

    def tree(self, indent, name):
        return "%snull" % _(indent) + n(name)


class Array(Expression):
    """an array literal: [a, b, ..., n]"""

    def __init__(self, token, elements):
        self.token = token
        self.elements = elements

    def tree(self, indent, name):
        return "%sarray\n%s" % (
            _(indent) + n(name),
            make_list_tree(indent + 1, self.elements, "elements")
        )


class Object(Expression):
    """an object literal: [a: b, x: y]"""

    def __init__(self, token, pairs):
        self.token = token
        self.pairs = pairs

    def tree(self, indent, name):
        return "%sobject\n%s" % (
            _(indent) + n(name),
            make_dict_tree(indent + 1, self.pairs, "pairs")
        )


class AssignExpression(Expression):
    """an assign expression"""

    def __init__(self, token, name, value):
        self.token = token
        self.name = name
        self.value = value

    def tree(self, indent, name):
        return "%sassign\n%s\n%s" % (
            _(indent) + n(name),
            self.name.tree(indent + 1, "name"),
            self.value.tree(indent + 1, "value")
        )


class DeclareExpression(Expression):
    """a declare expression"""

    def __init__(self, token, name, value):
        self.token = token
        self.name = name
        self.value = value

    def tree(self, indent, name):
        return "%sdeclare\n%s\n%s" % (
            _(indent) + n(name),
            self.name.tree(indent + 1, "name"),
            self.value.tree(indent + 1, "value")
        )


class PrefixExpression(Expression):
    """a prefix operator expression"""

    def __init__(self, token, operator, right):
        self.token = token
        self.operator = operator
        self.right = right

    def tree(self, indent, name):
        return "%sprefix (%s)\n%s" % (
            _(indent) + n(name),
            self.operator,
            self.right.tree(indent + 1, "right")
        )


class InfixExpression(Expression):
    """an infix operator expression"""

    def __init__(self, token, operator, left, right):
        self.token = token
        self.operator = operator
        self.left = left
        self.right = right

    def tree(self, indent, name):
        return "%sinfix (%s)\n%s\n%s" % (
            _(indent) + n(name),
            self.operator,
            self.left.tree(indent + 1, "left"),
            self.right.tree(indent + 1, "right")
        )


class Parameter(Expression):
    """a parameter in a function definition"""

    def __init__(self, token, name):
        self.token = token
        self.name = name

    def tree(self, indent, name):
        return "%s$%s" % (_(indent) + n(name), self.name)


class Argument(Expression):
    """an argument in a function call"""

    def __init__(self, token, value):
        self.token = token
        self.value = value

    def tree(self, indent, name):
        return "%sarg\n%s" % (
            _(indent) + n(name),
            self.value.tree(indent + 1, "value")
        )


class FunctionCall(Expression):
    """calls a function, using a pattern"""

    def __init__(self, token, pattern):
        self.token = token
        self.pattern = pattern

    def tree(self, indent, name):
        return "%sfn call\n%s" % (
            _(indent) + n(name),
            make_list_tree(indent + 1, self.pattern, "pattern")
        )


class IfExpression(Expression):
    """an if expression"""

    def __init__(self, token, condition, consequence, alternative):
        self.token = token
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def tree(self, indent, name):
        if self.e is None:
            return "%sif\n%s\n%s" % (
                _(indent) + n(name),
                self.condition.tree(indent + 1, "condition"),
                self.consequence.tree(indent + 1, "consequence")
            )

        return "%sif\n%s\n%s\n%s" % (
            _(indent) + n(name),
            self.condition.tree(indent + 1, "condition"),
            self.consequence.tree(indent + 1, "consequence"),
            self.alternative.tree(indent + 1, "alternative")
        )


class BlockLiteral(Expression):
    """a code block literal"""

    def __init__(self, token, body, params):
        self.token = token
        self.body = body
        self.params = params or []

    def tree(self, indent, name):
        return "%sblock\n%s\n%s" % (
            _(indent) + n(name),
            self.body.tree(indent + 1, "body"),
            make_list_tree(indent + 1, self.params, "params")
        )


class WhileLoop(Expression):
    """a while loop node"""

    def __init__(self, token, condition, body):
        self.token = token
        self.condition = condition
        self.body = body

    def tree(self, indent, name):
        return "%swhile\n%s\n%s" % (
            _(indent) + n(name),
            self.condition.tree(indent + 1, "condition"),
            self.body.tree(indent + 1, "body")
        )


class ForLoop(Expression):
    """a for loop node"""

    def __init__(self, token, var, collection, body):
        self.token = token
        self.var = var
        self.collection = collection
        self.body = body

    def tree(self, indent, name):
        return "%sfor\n%s\n%s\n%s" % (
            _(indent) + n(name),
            self.var.tree(indent + 1, "var"),
            self.collection.tree(indent + 1, "collection"),
            self.body.tree(indent + 1, "body")
        )


# Statements

class ExpressionStatement(Statement):
    """a statement containing a single expression"""

    def __init__(self, token, expr):
        self.token = token
        self.expr = expr

    def tree(self, indent, name):
        return self.expr.tree(indent, name)


class ReturnStatement(Statement):
    """returns a value from a function"""

    def __init__(self, token, expr):
        self.token = token
        self.expr = expr

    def tree(self, indent, name):
        return "%sreturn\n%s" % (
            _(indent) + n(name),
            self.expr.tree(indent + 1, "expr")
        )


class BlockStatement(Statement):
    """a list of statements"""

    def __init__(self, token, statements):
        self.token = token
        self.statements = statements

    def tree(self, indent, name):
        return "%sstmts\n%s" % (
            _(indent) + n(name),
            make_list_tree(indent + 1, self.statements, "statements")
        )


class FunctionDefinition(Statement):
    """
        defines a function.
        the pattern is an array, where each
        element is either an Identifier or
        a Parameter
    """

    def __init__(self, token, pattern, body):
        self.token = token
        self.pattern = pattern
        self.body = body

    def tree(self, indent, name):
        return "%sfunction\n%s\n%s" % (
            _(indent) + n(name),
            make_list_tree(indent + 1, self.pattern, "pattern"),
            self.body.tree(indent + 1, "body")
        )


class ReturnStatement(Statement):
    """a return statement"""

    def __init__(self, token, value):
        self.token = token
        self.value = value

    def tree(self, indent, name):
        if self.e is None:
            return "%sreturn" % (_(indent) + n(name))

        return "%sreturn\n%s" % (
            _(indent) + n(name),
            self.value.tree(indent + 1, "value")
        )


class NextStatement(Statement):
    """the next statement"""

    def __init__(self, token):
        self.token = token

    def tree(self, indent, name):
        return "%snext" % (_(indent) + n(name))


class BreakStatement(Statement):
    """the break statement"""

    def __init__(self, token):
        self.token = token

    def tree(self, indent, name):
        return "%sbreak" % (_(indent) + n(name))
