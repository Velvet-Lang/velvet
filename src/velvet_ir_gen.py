import json
from velvet_ast import AST, Node, VarNode, FuncNode, etc.  # Import all

class VelvetIRGen:
    def __init__(self, ast: AST):
        self.ast = ast
        self.ir = {}
        self.type_mappings = {
            'int': {'rust': 'i32', 'python': 'int', 'go': 'int'},
            'list<int>': {'rust': 'Vec<i32>', 'python': 'list', 'go': '[]int'},
            # Add more
        }

    def generate(self) -> Dict:
        self.ir['deps'] = self.ast.deps
        self.ir['imports'] = [i.path for i in self.ast.imports]
        self.ir['nodes'] = self.gen_nodes(self.ast.nodes)
        self.ir['inline'] = [(i.lang, i.code) for i in self.ast.inline]
        # Expand macros: Stub
        return self.ir

    def gen_nodes(self, nodes: List[Node]):
        ir_nodes = []
        for node in nodes:
            if isinstance(node, DecoratorNode):
                ir_nodes.append({'type': 'decorator', 'name': node.name, 'target': self.gen_nodes([node.target])})
            elif isinstance(node, VarNode):
                mapped_type = self.type_mappings.get(node.type, node.type)
                ir_nodes.append({'type': 'var', 'name': node.name, 'typ': mapped_type, 'expr': node.expr})
            elif isinstance(node, FuncNode):
                ir_nodes.append({'type': 'func', 'name': node.name, 'async': node.async_flag, 'params': self.gen_nodes(node.params), 'body': self.gen_nodes(node.body), 'ret': node.return_expr})
            elif isinstance(node, MacroNode):
                # Expand at IR? Stub
                ir_nodes.append({'type': 'macro', 'name': node.name, 'body': node.body})
            elif isinstance(node, MatchNode):
                ir_nodes.append({'type': 'match', 'expr': node.expr, 'cases': node.cases})
            elif isinstance(node, PatternNode):
                ir_nodes.append({'type': 'pattern', 'pat': node.pat, 'expr': node.expr})
            # Add more
        return ir_nodes

# Integrate with parser: after parse, gen = VelvetIRGen(ast).generate(); json.dump(gen, file)
