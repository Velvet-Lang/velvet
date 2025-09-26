import re
import json
from typing import List, Dict, Any
import ast
import subprocess

# BNF Grammar (simplified for MVP; migrate to nom/lalrpop in Rust)
# <program> ::= <deps> <stmts>
# <deps> ::= (<id>)*
# <stmts> ::= <stmt>*
# <stmt> ::= <var> | <func> | <if> | <loop> | <inline> | <comment>
# <var> ::= ~<id>=<expr>;
# <func> ::= !<id>(<params>){<stmts> ^<expr>?};
# <if> ::= ?<expr>{<stmts>};
# <loop> ::= *<id>=<expr>..<expr>{<stmts>};
# <inline> ::= #<lang>{<code>};
# <comment> ::= @<text>
# <expr> ::= <id> | <num> | <str> | <op><expr> | <expr><op><expr>
# Type Mapping: Velvet ~list -> Python list; ~str -> str; etc. (via context dict)

class VelvetParser:
    def __init__(self):
        self.tokens = []
        self.ast = {}
        self.dependencies = []
        self.inline_blocks = []
        self.type_map = {"~list": list, "~str": str, "~int": int, "~float": float}  # Inline mapping

    def tokenize(self, code: str) -> List[str]:
        code = re.sub(r'@.*?$', '', code, flags=re.MULTILINE)
        tokens = re.findall(r'[<>#~!?*^{};=+\-/\(\)\[\]0-9a-zA-Z"]+|".*?"', code)
        self.tokens = [t.strip() for t in tokens if t.strip()]
        return self.tokens

    def parse_dependencies(self):
        # Existing...

    def parse_inline(self, code: str):
        matches = re.findall(r'#(\w+)\s*\{(.*?)\}', code, re.DOTALL)
        for lang, block in matches:
            self.inline_blocks.append((lang, block))

    def parse_core(self):
        # Expanded: Build AST per BNF
        i = 0
        while i < len(self.tokens):
            tok = self.tokens[i]
            if tok == '~':  # Var
                # Parse ~x=5;
                self.ast.setdefault('vars', []).append({'type': 'var', 'tokens': self.tokens[i:i+3]})
                i += 3
            elif tok == '!':  # Func
                # Parse !add(~a,~b){^a+b};
                self.ast.setdefault('funcs', []).append({'type': 'func', 'tokens': self.tokens[i:]})
                break  # Simplified
            # Add for ?, *, etc.
            i += 1

    def generate_ir(self) -> Dict[str, Any]:
        ir = {
            'dependencies': self.dependencies,
            'inline': self.inline_blocks,
            'ast': self.ast,
            'types': self.type_map
        }
        return ir

    def parse(self, code: str, output_ir: str = None) -> Dict[str, Any]:
        self.tokenize(code)
        self.parse_dependencies()
        self.parse_inline(code)
        self.parse_core()
        result = self.generate_ir()
        if output_ir:
            with open(output_ir, 'w') as f:
                json.dump(result, f, indent=2)
        return result

# Usage...
if __name__ == '__main__':
    import sys
    code = sys.stdin.read() if not sys.argv[1:] else open(sys.argv[1]).read()
    parser = VelvetParser()
    result = parser.parse(code, output_ir='ir.json' if '--output-ir' in sys.argv else None)
    print(json.dumps(result, indent=2))
