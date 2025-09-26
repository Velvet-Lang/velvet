from velvet_lexer import VelvetLexer
from velvet_ast import *
from typing import List, Dict, Any
import re

# Updated BNF:
# <program> ::= <imports> <deps> <stmts>
# <imports> ::= import "<path>";*
# <deps> ::= <dep>*
# <stmt> ::= <decorator>* (<var> | <func> | <macro> | <match> | <pattern> | <if> | <loop> | <inline>)
# <var> ::= ~<id>(:<type>)?=<expr>;
# <type> ::= int | str | list<<type>> | ...
# <func> ::= (async)? !<id>(<params>){<stmts> ^<expr>?};
# <macro> ::= !macro <id> {<expansion>};
# <match> ::= match <expr> { <case>* _ => <stmt> };
# <case> ::= <pat> => <stmt>,
# <pattern> ::= let <pat> = <expr>;
# <inline> ::= #<lang>{<code>};
# Type mappings extended: list<int> -> Rust Vec<i32>, Python list, etc.

class VelvetParser:
    def __init__(self):
        self.lexer = VelvetLexer()
        self.tokens = []
        self.pos = 0
        self.ast = AST([], [], [], [])

    def parse(self, code: str) -> AST:
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
        self.parse_inline(code)  # Still regex for inline
        return self.ast

    def parse_imports(self):
        while self.peek() == 'IMPORT':
            self.consume('IMPORT')
            path = self.consume('STR')[1:-1]  # "path.vel"
            self.consume('SEMI')
            self.ast.imports.append(ImportNode(path))
            # Load and merge AST? Stub: assume single file

    def parse_deps(self):
        while self.peek() == 'DEP_START':
            self.consume('DEP_START')
            dep = self.consume('ID')
            self.consume('DEP_END')
            self.ast.deps.append(dep)

    def parse_decorators(self):
        decos = []
        while self.peek() == 'DECORATOR':
            decos.append(self.consume('DECORATOR')[1:])  # @inline -> inline
        return decos

    def parse_stmt(self):
        tok = self.peek()
        if tok == 'VAR':
            return self.parse_var()
        elif tok == 'FUNC' or self.peek(1) == 'FUNC':  # async !
            return self.parse_func()
        elif tok == 'MACRO':
            return self.parse_macro()
        elif tok == 'MATCH':
            return self.parse_match()
        elif tok == 'LET':
            return self.parse_pattern()
        # Add if, loop, etc.
        else:
            self.pos += 1
            return Node()  # Placeholder

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
            inner = self.parse_type()
            self.consume('>')
            return f"{base}<{inner}>"
        return base

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
            params.append(self.parse_var())  # Simplified
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
        body = ''  # Collect until }
        while self.peek() != 'RBRACE':
            body += self.tokens[self.pos][1] + ' '
            self.pos += 1
        self.consume('RBRACE')
        self.consume('SEMI')
        return MacroNode(name, body)

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
        return PatternNode(pat, expr)

    def parse_pat(self):
        # Stub: (x,y) or id
        return 'pat'  # Expand

    def parse_expr(self):
        # Stub: id op id, etc.
        return 'expr'

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

# Usage
if __name__ == '__main__':
    code = '''
    import "mod.vel";
    <std>
    @inline
    ~x: int = 5;
    async !fetch(){ await 1; ^2 };
    !macro inc { x + 1 };
    match y { 1 => print, _ => err };
    let (a,b) = point;
    #rust { println!("Hi"); }
    '''
    parser = VelvetParser()
    ast = parser.parse(code)
    print(ast)
