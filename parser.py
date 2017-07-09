import ast
import token

LOWEST      = 0  #
ASSIGN      = 1  # =
OR          = 2  # ||
AND         = 3  # &&
BIT_OR      = 4  # |
BIT_AND     = 5  # &
EQUALS      = 6  # == or !==
LESSGREATER = 7  # < or >
SUM         = 8  # + or -
PRODUCT     = 9  # * or /
PREFIX      = 10 # -x

precedences = {
    token.EQ:     EQUALS,
    token.N_EQ:   EQUALS,
    token.LT:     LESSGREATER,
    token.GT:     LESSGREATER,
    token.PLUS:   SUM,
    token.MINUS:  SUM,
    token.STAR:   PRODUCT,
    token.SLASH:  PRODUCT,
    token.ASSIGN: ASSIGN,
    token.OR:     OR,
    token.AND:    AND,
    token.B_OR:   BIT_OR,
    token.B_AND:  BIT_AND
}

class Parser(object):
    """parses a stream of tokens into an abstract syntax tree (AST)"""
    def __init__(self, tokens):
        self.tokens   = tokens
        self.errors  = [] # [(msg, start, end)]
        self.cur_tok  = None
        self.peek_tok = None
        
        self.prefixes = {
            # Literals
            token.ID:      self.parse_id,
            token.NUM:     self.parse_num,
            token.TRUE:    self.parse_bool,
            token.FALSE:   self.parse_bool,
            token.NULL:    self.parse_null,
            token.LSQUARE: self.parse_array,
            token.STR:     self.parse_string,
            
            # Prefix operators
            token.MINUS: self.parse_prefix,
            token.PLUS:  self.parse_prefix,
            
            # Constructs
            token.LPAREN: self.parse_grouped_expr,
            token.BSLASH: self.parse_function_call,
            token.IF:     self.parse_if_expr
        }
        
        self.infixes  = {
            token.PLUS:   self.parse_infix,
            token.MINUS:  self.parse_infix,
            token.STAR:   self.parse_infix,
            token.SLASH:  self.parse_infix,
            token.EQ:     self.parse_infix,
            token.N_EQ:   self.parse_infix,
            token.LT:     self.parse_infix,
            token.GT:     self.parse_infix,
            token.OR:     self.parse_infix,
            token.AND:    self.parse_infix,
            token.B_OR:   self.parse_infix,
            token.B_AND:  self.parse_infix,
            token.ASSIGN: self.parse_assign_expr
        }
        
        self.next()
        self.next()
        
    def peek_precedence(self):
        return precedences.get(self.peek_tok.type, LOWEST)
        
    def cur_precedence(self):
        return precedences.get(self.cur_tok.type, LOWEST)
        
    def peek_err(self, t):
        if type(t) == type([]):
            msg = "expected any of [%s], but got %s" % (
                ("".join(str(ty) + ", " for ty in t))[:-2],
                self.peek_tok.type
            )
        else:
            msg = "expected %s, but got %s" % (t, self.peek_tok.type)
            
        self.err(msg, self.peek_tok.start, self.peek_tok.end)
        
    def cur_err(self, t):
        if type(t) == type([]):
            msg = "expected any of [%s], but got %s" % (
                ("".join(str(ty) + ", " for ty in t))[:-2],
                self.cur_tok.type
            )
        else:
            msg = "expected %s, but got %s" % (t, self.cur_tok.type)
            
        self.err(msg)
        
    def no_prefix_fn_error(self, t):
        msg = "unexpected token: %s" % t
        self.err(msg)
        
    def err(self, msg, start = None, end = None):
        if start == None:
            start = self.cur_tok.start
            
        if end == None:
            end = self.cur_tok.end
        
        error = (msg, start, end)
        self.errors.append(error)
        
    def print_error(self, index = 0):
        msg, start, end = self.errors[index]
        
        print('[%s:%s] to [%s:%s] -- %s' % (
            start[0], start[1],
            end[0], end[1],
            msg
        ))
        
    def print_errors(self):
        for i in range(len(self.errors)):
            self.print_error(i)
        
    def next(self):
        self.cur_tok = self.peek_tok
        self.peek_tok = next(self.tokens)
        
        if self.peek_tok.type == token.ILLEGAL:
            self.err("illegal token found: '%s'" % self.peek_tok.literal, self.peek_tok.start, self.peek_tok.end)
        
    def parse_program(self):
        prog = ast.Program([])
        
        while not self.cur_is(token.EOF):
            stmt = self.parse_stmt()
            
            if stmt != None:
                prog.statements.append(stmt)
                
            self.next()
            
        return prog
        
    def parse_stmt(self):
        stmt = None
        
        if self.cur_is(token.SEMI):
            return None
        elif self.cur_is(token.RETURN):
            stmt = self.parse_return_stmt()
        elif self.cur_is(token.DEF):
            stmt = self.parse_def_stmt()
        else:
            stmt = self.parse_expr_stmt()
            
        if not self.expect(token.SEMI):
            return None
            
        return stmt
        
    def parse_block_statement(self):
        block = ast.BlockStatement(self.cur_tok, [])
        
        self.next()
        
        while not self.cur_is(token.RBRACE) and not self.cur_is(token.EOF):
            stmt = self.parse_stmt()
            
            if stmt != None:
                block.statements.append(stmt)
                
            self.next()
            
        return block
        
    def parse_expr_stmt(self):
        return ast.ExpressionStatement(self.cur_tok, self.parse_expr(LOWEST))
        
    def parse_return_stmt(self):
        if self.peek_tok.type == token.SEMI:
            return ast.ReturnStatement(self.cur_tok, None)
            
        stmt = ast.ReturnStatement(self.cur_tok, None)
        self.next()
        stmt.value = self.parse_expr(LOWEST)
        
        return stmt
        
    def parse_def_stmt(self):
        stmt = ast.FunctionDefinition(self.cur_tok, [], None)
        
        self.next()
        
        while not self.cur_is(token.LBRACE):
            tok = self.cur_tok
                                  
            if not self.expect_cur_any([token.ID, token.PARAM]):
                return None
                                
            if tok.type == token.ID:
                stmt.pattern.append(ast.Identifier(tok))
            else:
                stmt.pattern.append(ast.Parameter(tok, tok.literal))
            
        stmt.body = self.parse_block_statement()
        
        if len(stmt.pattern) == 0:
            self.err("expected at least one item in a pattern")
            return None
                
        return stmt
        
    def parse_expr(self, precedence):
        prefix = self.prefixes.get(self.cur_tok.type, None)
        
        if prefix == None:
            self.no_prefix_fn_error(self.cur_tok.type)
            return None
            
        left = prefix()
        
        while not self.peek_is(token.SEMI) and precedence < self.peek_precedence():
            infix = self.infixes.get(self.peek_tok.type, None)
            
            if infix == None:
                return left
                
            self.next()
            
            left = infix(left)
            
        return left
        
    def parse_id(self):
        return ast.Identifier(self.cur_tok)
        
    def parse_num(self):
        lit = ast.Number(self.cur_tok, None)
        
        try:
            lit.value = float(self.cur_tok.literal)
        except ValueError:
            msg = "could not parse %s as a number" % self.cur_tok.literal
            self.err(msg)
            return None
            
        return lit
        
    def parse_bool(self):
        return ast.Boolean(self.cur_tok, self.cur_tok.type == token.TRUE)
        
    def parse_null(self):
        return ast.Null(self.cur_tok)
        
    def parse_string(self):
        return ast.String(self.cur_tok)
        
    def parse_prefix(self):
        expr = ast.PrefixExpression(self.cur_tok, self.cur_tok.literal, None)
        
        self.next()
        
        expr.right = self.parse_expr(PREFIX)
        
        return expr
        
    def parse_grouped_expr(self):
        self.next()
        
        expr = self.parse_expr(LOWEST)
        
        if not self.expect(token.RPAREN):
            return None
            
        return expr
        
    def parse_array(self):
        return ast.Array(self.cur_tok, self.parse_expr_list(token.RSQUARE))
        
    def parse_function_call(self):
        expr = ast.FunctionCall(self.cur_tok, [])
        
        while self.peek_in([token.ID, token.LPAREN]):
            self.next()
            
            if self.cur_is(token.ID):
                expr.pattern.append(self.parse_id())
            elif self.cur_is(token.LPAREN):
                arg = ast.Argument(self.cur_tok, None)
                
                self.next()
                arg.value = self.parse_expr(LOWEST)
                
                if not self.expect(token.RPAREN):
                    return None
                    
                expr.pattern.append(arg)
                
        if len(expr.pattern) == 0:
            self.err("expected at least one item in a pattern")
            return None
                                
        return expr
        
    def parse_if_expr(self):
        expr = ast.IfExpression(self.cur_tok, None, None, None)
        
        self.next()
        expr.condition = self.parse_expr(LOWEST)
        
        if not self.expect(token.LBRACE):
            return None
            
        expr.consequence = self.parse_block_statement()
        
        if self.peek_is(token.ELSE):
            self.next()
            
            if not self.expect(token.LBRACE):
                return None
                
            expr.alternative = self.parse_block_statement()
        elif self.peek_is(token.ELIF):
            self.next()
            
            expr.alternative = ast.BlockStatement(
                self.cur_tok,
                [ast.ExpressionStatement(self.cur_tok, self.parse_if_expr())]
            )
            
        return expr
        
    def parse_infix(self, left):
        expr = ast.InfixExpression(self.cur_tok, self.cur_tok.literal, left, None)
        
        precedence = self.cur_precedence()
        self.next()
        expr.right = self.parse_expr(precedence)
        
        return expr
        
    def parse_assign_expr(self, left):
        expr = ast.AssignExpression(self.cur_precedence, left, None)
        
        self.next()
        expr.value = self.parse_expr(LOWEST)
        
        return expr
        
    def parse_expr_list(self, end):
        exprs = []

        if self.peek_is(end):
            self.next()
            return exprs
            
        self.next()
        exprs.append(self.parse_expr(LOWEST))
        
        while self.peek_is(token.COMMA):
            self.next()
            self.next()
            exprs.append(self.parse_expr(LOWEST))
            
        if not self.expect(end):
            return None
            
        return exprs
        
    def cur_is(self, t):
        return self.cur_tok.type == t
        
    def peek_is(self, t):
        return self.peek_tok.type == t
        
    def cur_in(self, t):
        return self.cur_tok.type in t
        
    def peek_in(self, t):
        return self.peek_tok.type in t
        
    def expect(self, t):
        if self.peek_is(t):
            self.next()
            return True
        else:
            self.peek_err(t)
            return False
            
    def expect_cur_any(self, ts):
        if self.cur_in(ts):
            self.next()
            return True
        else:
            self.cur_err(ts)
            return False
            
    def expect_peek_any(self, ts):
        if self.peek_in(ts):
            self.next()
            return True
        else:
            self.peek_err(ts)
            return False
