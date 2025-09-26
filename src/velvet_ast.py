from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class Node:
    pass

@dataclass
class VarNode(Node):
    name: str
    type: Optional[str] = None
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
    pat: Any
    expr: Any

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
class AST:
    deps: List[str]
    imports: List[ImportNode]
    nodes: List[Node]
    inline: List[InlineNode]
