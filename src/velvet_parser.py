import re
from typing import List, Dict, Any
import ast  # For inline Python eval (demo only; use safely)
import subprocess  # For other langs

class VelvetParser:
    def __init__(self):
        self.tokens = []
        self.ast = {}
        self.dependencies = []
        self.inline_blocks = []

    def tokenize(self, code: str) -> List[str]:
        # Simple tokenizer: split on symbols, ignore whitespace
        code = re.sub(r'@.*?$', '', code, flags=re.MULTILINE)  # Strip comments
        tokens = re.findall(r'[<>#~!?*^{};=+\-/\(\)\[\]0-9a-zA-Z"]+|".*?"', code)
        self.tokens = [t.strip() for t in tokens if t.strip()]
        return self.tokens

    def parse_dependencies(self):
        i = 0
        while i < len(self.tokens):
            if self.tokens[i] == '<':
                i += 1
                if i < len(self.tokens):
                    dep = self.tokens[i].strip('>')
                    self.dependencies.append(dep)
            i += 1

    def parse_inline(self, code: str):
        # Extract #lang { code }
        matches = re.findall(r'#(\w+)\s*\{(.*?)\}', code, re.DOTALL)
        for lang, block in matches:
            self.inline_blocks.append((lang, block))
            # Demo exec (non-prod)
            if lang == 'python':
                try:
                    exec(block)
                except Exception as e:
                    print(f"Inline Python error: {e}")
            elif lang == 'shell':
                subprocess.run(block, shell=True)
            # Add more langs as needed

    def parse_core(self):
        # Placeholder for Velvet AST: ~var=val; !func{...}; ?cond{...}; *loop{...}
        self.ast['vars'] = []
        self.ast['funcs'] = []
        self.ast['conds'] = []
        self.ast['loops'] = []
        # ... expand with full parser logic

    def parse(self, code: str) -> Dict[str, Any]:
        self.tokenize(code)
        self.parse_dependencies()
        self.parse_inline(code)
        self.parse_core()
        return {
            'dependencies': self.dependencies,
            'inline': self.inline_blocks,
            'ast': self.ast
        }

# Usage example
if __name__ == '__main__':
    sample_code = """
    <std> <math>
    @ This is a comment
    ~x=5;
    !add(~a,~b){^a+b};
    ?x>0{
        *i=0..x{add(i,1)}
    }
    #python {
        print("Inline Python!")
    }
    #shell {
        echo "Inline Shell!"
    }
    """
    parser = VelvetParser()
    result = parser.parse(sample_code)
    print(result)
