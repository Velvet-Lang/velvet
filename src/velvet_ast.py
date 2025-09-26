from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Node:
    pass

@dataclass
class TypeNode(Node):
    base: str
    params: List['TypeNode'] = field(default_factory=list)  # For generics

@dataclass
class MapType(TypeNode):
    key: TypeNode
    val: TypeNode

@dataclass
class SetType(TypeNode):
    elem: TypeNode

@dataclass
class TupleType(TypeNode):
    elems: List[TypeNode]

@dataclass
class VarNode(Node):
    name: str
    type: Optional[TypeNode] = None
    expr: Any = None

@dataclass
class FuncNode(Node):
    name: str
    params: List[VarNode]
    body: List[Node]
    return_expr: Optional[Any] = None
    async_flag: bool = False

@dataclass
class MacroNode(Node):
    name: str
    body: str  # Expansion code

@dataclass
class MatchNode(Node):
    expr: Any
    cases: List[Dict[str, Any]]  # pat => stmt

@dataclass
class PatternNode(Node):
    kind: str  # 'var', 'tuple', 'list', 'dict'
    parts: List[Any]  # Sub-patterns/values

@dataclass
class ImportNode(Node):
    path: str

@dataclass
class DecoratorNode(Node):
    name: str
    target: Node

@dataclass
class InlineNode(Node):
    lang: str
    code: str

@dataclass
class IfNode(Node):
    cond: Any
    body: List[Node]

@dataclass
class LoopNode(Node):
    var: str
    start: Any
    end: Any
    body: List[Node]

@dataclass
class AST:
    deps: List[str]
    imports: List[ImportNode]
    nodes: List[Node]
    inline: List[InlineNode]
