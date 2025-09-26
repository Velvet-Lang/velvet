import re

class VelvetLexer:
    def __init__(self):
        self.token_specs = [
            ('DEP_START', r'<'), ('DEP_END', r'>'),
            ('VAR', r'~'), ('FUNC', r'!'), ('IF', r'\?'), ('LOOP', r'\*'),
            ('MATCH', r'match'), ('LET', r'let'), ('ASYNC', r'async'),
            ('AWAIT', r'await'), ('IMPORT', r'import'),
            ('DECORATOR', r'@[\w]+'), ('MACRO', r'!macro'),
            ('INLINE', r'#[\w]+'), ('LBRACE', r'{'), ('RBRACE', r'}'),
            ('LPAREN', r'\('), ('RPAREN', r'\)'), ('COMMA', r','),
            ('EQ', r'='), ('COLON', r':'), ('SEMI', r';'),
            ('ARROW', r'=>'), ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('NUM', r'\d+'), ('STR', r'".*?"'), ('OP', r'[+\-*/]'),
            ('COMMENT', r'@.*?$'),
        ]
        self.token_re = re.compile('|'.join(f'(?P<{name}>{pat})' for name, pat in self.token_specs), re.MULTILINE)

    def lex(self, code: str):
        tokens = []
        for mo in self.token_re.finditer(code):
            kind = mo.lastgroup
            value = mo.group()
            if kind != 'COMMENT':
                tokens.append((kind, value))
        return tokens
