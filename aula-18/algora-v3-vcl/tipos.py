from enum import Enum, auto
from dataclasses import dataclass
from itertools import chain
from itertools import islice
from typing import Callable, Optional

class TokenType(Enum):
    INTEIRO = auto()
    ADD = auto()
    SUB = auto()
    MULT = auto()
    DIV = auto()
    POW = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    COMMA = auto()
    COLON = auto()       # :
    DOT = auto()         # .
    ASSIGN = auto()      # :=
    EQUAL = auto()       # =
    EQEQ = auto()        # ==
    LT = auto()          # <
    NOME = auto()
    VAR = auto()         # var
    FUNCTION = auto()    # function
    FN = auto()          # fn
    IF = auto()          # if
    ELSE = auto()        # else
    WHILE = auto()       # while

@dataclass(frozen=True)
class Token:
    type: TokenType
    lexema: str

@dataclass(frozen=True)
class Erro:
    msg: str

def monadic_error(func):
    def wrapper(tokens, *args, **kwargs):
        if isinstance(tokens, Erro):
            return tokens
        return func(tokens, *args, **kwargs)
    return wrapper

# --- Estrutura de Nós da AST com Dataclasses ---

class Stmt: pass
class Expr: pass

@dataclass(frozen=True)
class VarDecl(Stmt):
    name: str
    init_expr: Expr

@dataclass(frozen=True)
class Assign(Stmt):
    name: str
    value_expr: Expr

@dataclass(frozen=True)
class AssignField(Stmt):
    obj_expr: Expr      # e_o em `e_o.f := e`
    name: str           # f
    value_expr: Expr    # e

@dataclass(frozen=True)
class FunDecl(Stmt):
    name: str
    params: list[str]
    body: "Block"

@dataclass(frozen=True)
class ExprStmt(Stmt):
    expr: Expr

@dataclass(frozen=True)
class While(Stmt):
    cond: Expr
    body: list[Stmt]    # bloco_cmd: sequência de comandos, sem expressão final

@dataclass(frozen=True)
class Num(Expr):
    value: int | float

@dataclass(frozen=True)
class Var(Expr):
    name: str

@dataclass(frozen=True)
class AnonFun(Expr):
    params: list[str]
    body: "Block"

@dataclass(frozen=True)
class Call(Expr):
    callee: Expr
    args: list[Expr]

@dataclass(frozen=True)
class Record(Expr):
    fields: list[tuple[str, Expr]]   # { f1: e1, ..., fn: en }, nomes distintos

@dataclass(frozen=True)
class Field(Expr):
    obj_expr: Expr
    name: str

@dataclass(frozen=True)
class BinaryOp(Expr):
    op: str
    left: Expr
    right: Expr

@dataclass(frozen=True)
class UnaryOp(Expr):
    op: str
    operand: Expr

@dataclass(frozen=True)
class IfExpr(Expr):
    cond: Expr
    then_block: "Block"
    else_block: "Block"

@dataclass(frozen=True)
class Block(Expr):
    stmts: list[Stmt]
    final_expr: Expr

type Ast = Block | Stmt | Expr

# --- Predicados para o Parser ---

def match_type(*types: TokenType) -> Callable[[Optional[Token]], Optional[Token]]:
    def predicate(tok: Optional[Token]) -> Optional[Token]:
        if tok and tok.type in types:
            return tok
        return None
    return predicate

LPAREN    = match_type(TokenType.LPAREN)
RPAREN    = match_type(TokenType.RPAREN)
LBRACE    = match_type(TokenType.LBRACE)
RBRACE    = match_type(TokenType.RBRACE)
SEMICOLON = match_type(TokenType.SEMICOLON)
COMMA     = match_type(TokenType.COMMA)
COLON     = match_type(TokenType.COLON)
DOT       = match_type(TokenType.DOT)
INTEIRO  = match_type(TokenType.INTEIRO)
NOME      = match_type(TokenType.NOME)
VAR       = match_type(TokenType.VAR)
FUNCTION  = match_type(TokenType.FUNCTION)
FN        = match_type(TokenType.FN)
IF        = match_type(TokenType.IF)
ELSE      = match_type(TokenType.ELSE)
WHILE     = match_type(TokenType.WHILE)
ASSIGN    = match_type(TokenType.ASSIGN)
EQUAL     = match_type(TokenType.EQUAL)
EQEQ      = match_type(TokenType.EQEQ)
LT        = match_type(TokenType.LT)
POW       = match_type(TokenType.POW)

OPS_ADIT  = match_type(TokenType.ADD, TokenType.SUB)
OPS_MULT  = match_type(TokenType.MULT, TokenType.DIV)
UNARIO    = match_type(TokenType.ADD, TokenType.SUB)

class Stream:
    def __init__(self, tokens: list[Token]):
        self.it = iter(tokens)
        self.anterior: Optional[Token] = None   # último token consumido

    def peek(self, k: int = 0) -> Optional[Token]:
        """Espia o k-ésimo token a partir do atual (k = 0 é o próximo), sem consumir."""
        janela = list(islice(self.it, k + 1))
        self.it = chain(janela, self.it)
        return janela[k] if len(janela) > k else None

    def next(self) -> Optional[Token]:
        try:
            self.anterior = next(self.it)
        except StopIteration:
            return None
        return self.anterior
