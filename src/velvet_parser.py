import re
from collections import deque
from velvet_lexer import VelvetLexer
from velvet_ast import *
from weave.helpers import expand_macros

# Updated BNF (simplified):
# <program> ::= <imports> <deps> <stmts>
# <imports> ::= import "<path>";*
# <deps> ::= <dep>*
# <stmt> ::= <decorator>* (<var> | <func> | <macro> | <match> | <pattern> | <if> | <loop> | <inline>)
# <var> ::= ~<id>(:<type>)?=<expr>;
# <type> ::= int | str | list<<type>> | map<<type>,<type>> | set<<type>> | tuple<<type>[,<type>]*> | ...
# <func> ::= (async)? !<id>(<params>){<stmts> ^<expr>?};
# <macro> ::= !macro <id> {<expansion>};
# <match> ::= match <expr> { <case>* _ => <stmt> };
# <case> ::= <pat> => <stmt>,
# <pattern> ::= let <pat> = <expr>;
# <if> ::= ?<expr>{<stmts>};
# <loop> ::= *<id>=<expr>..<expr>{<stmts>};
# <inline> ::= #<lang>{<code>};

class VelvetParser:
    def __init__(self):
        self.lexer = VelvetLexer()
        self.tokens = []
        self.pos = 0
        self.ast = AST([], [], [], [])
        self.macros = {}  # name: body for expansion

    def parse(self, code: str) -> AST:
        code = expand_macros(code, self.macros)  # Pre-expand macros
        self.tokens = self.lexer.lex(code)
        self.parse_imports()
        self.parse_deps()
        while self.pos < len(self.tokens):
            decos = self.parse_decorators()
            stmt = self.parse_stmt()
            if decos:
                for deco in reversed(decos):
                    stmt = DecoratorNode(deco, stmt)
            self.ast.nodes.append(stmt)
        self.parse_inline(code)  # Regex for inline
        return self.ast

    def parse_imports(self):
        while self.peek() == 'IMPORT':
            self.consume('IMPORT')
            path = self.consume('STR')[1:-1]
            self.consume('SEMI')
            self.ast.imports.append(ImportNode(path))

    def parse_deps(self):
        while self.peek() == 'DEP_START':
            self.consume('DEP_START')
            dep = self.consume('ID')
            self.consume('DEP_END')
            self.ast.deps.append(dep)

    def parse_decorators(self):
        decos = []
        while self.peek() == 'DECORATOR':
            decos.append(self.consume('DECORATOR')[1:])
        return decos

    def parse_stmt(self):
        tok = self.peek()
        if tok == 'VAR':
            return self.parse_var()
        elif tok in {'FUNC', 'ASYNC'}:
            return self.parse_func()
        elif tok == 'MACRO':
            return self.parse_macro()
        elif tok == 'MATCH':
            return self.parse_match()
        elif tok == 'LET':
            return self.parse_pattern()
        elif tok == 'IF':
            return self.parse_if()
        elif tok == 'LOOP':
            return self.parse_loop()
        else:
            self.pos += 1
            return Node()

    def parse_var(self):
        self.consume('VAR')
        name = self.consume('ID')
        typ = None
        if self.peek() == 'COLON':
            self.consume('COLON')
            typ = self.parse_type()
        self.consume('EQ')
        expr = self.parse_expr()
        self.consume('SEMI')
        return VarNode(name, typ, expr)

    def parse_type(self):
        base = self.consume('ID')
        if self.peek() == '<':
            self.consume('<')
            params = []
            while self.peek() != '>':
                params.append(self.parse_type())
                if self.peek() == 'COMMA': self.consume('COMMA')
            self.consume('>')
            if base == 'list':
                return TypeNode('list', params)
            elif base == 'map':
                return MapType(params[0], params[1])
            elif base == 'set':
                return SetType(params[0])
            elif base == 'tuple':
                return TupleType(params)
        return TypeNode(base)

    def parse_func(self):
        async_flag = False
        if self.peek() == 'ASYNC':
            async_flag = True
            self.consume('ASYNC')
        self.consume('FUNC')
        name = self.consume('ID')
        self.consume('LPAREN')
        params = []
        while self.peek() != 'RPAREN':
            params.append(self.parse_var())
            if self.peek() == 'COMMA': self.consume('COMMA')
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = []
        while self.peek() != 'RBRACE' and self.peek() != '^':
            body.append(self.parse_stmt())
        ret = None
        if self.peek() == '^':
            self.consume('^')
            ret = self.parse_expr()
        self.consume('RBRACE')
        self.consume('SEMI')
        return FuncNode(name, params, body, ret, async_flag)

    def parse_macro(self):
        self.consume('MACRO')
        name = self.consume('ID')
        self.consume('LBRACE')
        body = ''
        while self.peek() != 'RBRACE':
            body += self.tokens[self.pos][1] + ' '
            self.pos += 1
        self.consume('RBRACE')
        self.consume('SEMI')
        macro = MacroNode(name, body)
        self.macros[name] = body  # For expansion
        return macro

    def parse_match(self):
        self.consume('MATCH')
        expr = self.parse_expr()
        self.consume('LBRACE')
        cases = []
        while self.peek() != 'RBRACE':
            pat = self.parse_pat()
            self.consume('ARROW')
            stmt = self.parse_stmt()
            cases.append({'pat': pat, 'stmt': stmt})
            if self.peek() == 'COMMA': self.consume('COMMA')
        self.consume('RBRACE')
        self.consume('SEMI')
        return MatchNode(expr, cases)

    def parse_pattern(self):
        self.consume('LET')
        pat = self.parse_pat()
        self.consume('EQ')
        expr = self.parse_expr()
        self.consume('SEMI')
        return PatternNode(pat.kind, pat.parts)  # Adjusted

    def parse_if(self):
        self.consume('IF')
        cond = self.parse_expr()
        self.consume('LBRACE')
        body = []
        while self.peek() != 'RBRACE':
            body.append(self.parse_stmt())
        self.consume('RBRACE')
        self.consume('SEMI')
        return IfNode(cond, body)

    def parse_loop(self):
        self.consume('LOOP')
        var = self.consume('ID')
        self.consume('EQ')
        start = self.parse_expr()
        self.consume('..')
        end = self.parse_expr()
        self.consume('LBRACE')
        body = []
        while self.peek() != 'RBRACE':
            body.append(self.parse_stmt())
        self.consume('RBRACE')
        self.consume('SEMI')
        return LoopNode(var, start, end, body)

    def parse_pat(self):
        if self.peek() == 'LPAREN':
            self.consume('LPAREN')
            parts = []
            while self.peek() != 'RPAREN':
                parts.append(self.parse_pat())
                if self.peek() == 'COMMA': self.consume('COMMA')
            self.consume('RPAREN')
            return PatternNode('tuple', parts)
        elif self.peek() == 'LBRACKET':
            self.consume('LBRACKET')
            parts = []
            while self.peek() != 'RBRACKET':
                parts.append(self.parse_pat())
                if self.peek() == 'COMMA': self.consume('COMMA')
            self.consume('RBRACKET')
            return PatternNode('list', parts)
        elif self.peek() == 'LBRACE':
            self.consume('LBRACE')
            parts = []
            while self.peek() != 'RBRACE':
                key = self.parse_expr()
                self.consume('COLON')
                val = self.parse_pat()
                parts.append((key, val))
                if self.peek() == 'COMMA': self.consume('COMMA')
            self.consume('RBRACE')
            return PatternNode('dict', parts)
        else:
            name = self.consume('ID')
            return PatternNode('var', [name])

    def parse_expr(self):
        output = deque()
        ops = deque()
        prec = {'+': 1, '-': 1, '*': 2, '/': 2}
        while self.pos < len(self.tokens) and self.peek() not in {';', '}', ',', 'ARROW'}:
            tok, val = self.tokens[self.pos]
            if tok in {'ID', 'NUM', 'STR'}:
                output.append(val)
            elif tok == 'LPAREN':
                ops.append('(')
            elif tok == 'RPAREN':
                while ops and ops[-1] != '(':
                    output.append(ops.pop())
                ops.pop()
            elif tok == 'OP':
                while ops and ops[-1] != '(' and prec.get(ops[-1], 0) >= prec[val]:
                    output.append(ops.pop())
                ops.append(val)
            # Func call: id( args )
            elif tok == 'ID' and self.peek(1) == 'LPAREN':
                func_name = val
                self.pos += 1  # Consume ID
                self.consume('LPAREN')
                args = []
                while self.peek() != 'RPAREN':
                    args.append(self.parse_expr())
                    if self.peek() == 'COMMA': self.consume('COMMA')
                self.consume('RPAREN')
                output.append({'call': func_name, 'args': args})
            self.pos += 1
        while ops:
            output.append(ops.pop())
        return list(output)

    def parse_inline(self, code: str):
        matches = re.findall(r'#(\w+)\s*\{(.*?)\}', code, re.DOTALL)
        for lang, block in matches:
            self.ast.inline.append(InlineNode(lang, block))

    def peek(self, offset=0):
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset][0]
        return None

    def consume(self, expected):
        tok, val = self.tokens[self.pos]
        if tok == expected:
            self.pos += 1
            return val
        raise ValueError(f"Expected {expected}, got {tok}")

if __name__ == '__main__':
    import sys
    code = sys.stdin.read() if not sys.argv[1:] else open(sys.argv[1]).read()
    parser = VelvetParser()
    ast = parser.parse(code)
    print(ast)
