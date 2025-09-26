import json
from velvet_ast import *

class VelvetIRGen:
    def __init__(self, ast: AST):
        self.ast = ast
        self.ir = {}
        self.type_mappings = {
            'int': {
                'rust': 'i32', 'python': 'int', 'go': 'int', 'crystal': 'Int32', 'ruby': 'Integer', 
                'c': 'int', 'cpp': 'int', 'csharp': 'int', 'julia': 'Int', 'zig': 'i32', 
                'lua': 'number', 'java': 'int', 'javascript': 'number', 'shell': 'int', 'powershell': 'int'
            },
            'str': {
                'rust': '&str', 'python': 'str', 'go': 'string', 'crystal': 'String', 'ruby': 'String', 
                'c': 'char*', 'cpp': 'std::string', 'csharp': 'string', 'julia': 'String', 'zig': '[]const u8', 
                'lua': 'string', 'java': 'String', 'javascript': 'string', 'shell': 'string', 'powershell': 'string'
            },
            'list<T>': {
                'rust': 'Vec<T>', 'python': 'list', 'go': '[]T', 'crystal': 'Array(T)', 'ruby': 'Array', 
                'c': 'array', 'cpp': 'std::vector<T>', 'csharp': 'List<T>', 'julia': 'Vector{T}', 'zig': '[]T', 
                'lua': 'table', 'java': 'List<T>', 'javascript': 'array', 'shell': 'array', 'powershell': 'array'
            },
            'map<K,V>': {
                'rust': 'HashMap<K,V>', 'python': 'dict', 'go': 'map[K]V', 'crystal': 'Hash(K,V)', 'ruby': 'Hash', 
                'c': 'map', 'cpp': 'std::map<K,V>', 'csharp': 'Dictionary<K,V>', 'julia': 'Dict{K,V}', 'zig': 'std.HashMap(K,V)', 
                'lua': 'table', 'java': 'Map<K,V>', 'javascript': 'object', 'shell': 'assoc', 'powershell': 'hashtable'
            },
            'set<T>': {
                'rust': 'HashSet<T>', 'python': 'set', 'go': 'map[T]struct{}', 'crystal': 'Set(T)', 'ruby': 'Set', 
                'c': 'set', 'cpp': 'std::set<T>', 'csharp': 'HashSet<T>', 'julia': 'Set{T}', 'zig': 'std.HashSet(T)', 
                'lua': 'table', 'java': 'Set<T>', 'javascript': 'Set', 'shell': 'set', 'powershell': 'hashset'
            },
            'tuple<T1,T2>': {
                'rust': '(T1,T2)', 'python': 'tuple', 'go': 'struct{T1;T2}', 'crystal': 'Tuple(T1,T2)', 'ruby': 'Array', 
                'c': 'struct', 'cpp': 'std::tuple<T1,T2>', 'csharp': 'Tuple<T1,T2>', 'julia': 'Tuple{T1,T2}', 'zig': 'struct {T1, T2}', 
                'lua': 'table', 'java': 'Pair<T1,T2>', 'javascript': 'array', 'shell': 'array', 'powershell': 'array'
            },
            # Add more types as needed
        }

    def generate(self) -> Dict:
        self.ir['deps'] = self.ast.deps
        self.ir['imports'] = [i.path for i in self.ast.imports]
        self.ir['nodes'] = self.gen_nodes(self.ast.nodes)
        self.ir['inline'] = [{'lang': i.lang, 'code': i.code, 'embed': True} for i in self.ast.inline]
        return self.ir

    def gen_nodes(self, nodes: List[Node]):
        ir_nodes = []
        for node in nodes:
            if isinstance(node, DecoratorNode):
                ir_nodes.append({'type': 'decorator', 'name': node.name, 'target': self.gen_nodes([node.target])[0]})
            elif isinstance(node, VarNode):
                mapped_type = {lang: self.type_mappings.get(node.type.base, {}).get(lang, node.type.base) for lang in self.type_mappings['int']}
                ir_nodes.append({'type': 'var', 'name': node.name, 'typ': mapped_type, 'expr': node.expr})
            elif isinstance(node, FuncNode):
                ir_nodes.append({'type': 'func', 'name': node.name, 'async': node.async_flag, 'params': self.gen_nodes(node.params), 'body': self.gen_nodes(node.body), 'ret': node.return_expr})
            elif isinstance(node, MacroNode):
                ir_nodes.append({'type': 'macro', 'name': node.name, 'body': node.body})
            elif isinstance(node, MatchNode):
                ir_nodes.append({'type': 'match', 'expr': node.expr, 'cases': node.cases})
            elif isinstance(node, PatternNode):
                ir_nodes.append({'type': 'pattern', 'kind': node.kind, 'parts': node.parts})
            elif isinstance(node, IfNode):
                ir_nodes.append({'type': 'if', 'cond': node.cond, 'body': self.gen_nodes(node.body)})
            elif isinstance(node, LoopNode):
                ir_nodes.append({'type': 'loop', 'var': node.var, 'start': node.start, 'end': node.end, 'body': self.gen_nodes(node.body)})
        return ir_nodes

if __name__ == '__main__':
    # Usage: python velvet_ir_gen.py <ast.json> > ir.json
    pass
