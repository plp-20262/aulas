from enum import Enum, auto
from dataclasses import dataclass
from itertools import chain
from typing import Callable, Optional, Any

type Ast = int | Token | list[Ast]

class TokenType(Enum):
    INTEIRO = auto()
    ADD = auto()
    SUB = auto()
    MULT = auto()
    DIV = auto()
    POW = auto()
    LPAREN = auto()
    RPAREN = auto()
    NOME = auto()
    LET = auto()
    IN = auto()
    EQUAL = auto()
    # aljabr v2 (§1): três novas categorias léxicas para lambdas e
    # aplicações: FN (palavra reservada `fn`), ARROW (`=>`) e COMMA (`,`)
    FN = auto()
    ARROW = auto()
    COMMA = auto()
    # aljabr v3 (§1): quatro novas palavras reservadas (letrec, if, then,
    # else) e dois novos operadores (==, <)
    LETREC = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    EQEQ = auto()
    LT = auto()
    # church v1 (§4.1): novas categorias léxicas para o sistema de tipos
    COLON = auto()          # :
    TARROW = auto()         # ->  (seta de tipo; deve casar antes de SUB)
    TNUM = auto()           # Num
    TBOOL = auto()          # Bool
    VERDADEIRO = auto()     # palavra reservada `verdadeiro`
    FALSO = auto()          # palavra reservada `falso`

@dataclass(frozen=True)
class Token:
    type: TokenType
    lexema: str

@dataclass(frozen=True)
class Erro:
    msg: str

# church v1 (§4.3): a "segunda sintaxe abstrata" — os tipos.
#   τ ::= Num | Bool | (τ₁, …, τₙ) -> τ   (n ≥ 0)
# São dataclasses imutáveis para que a igualdade seja estrutural (§4.3):
# dois tipos são iguais quando são a mesma árvore. O verificador usa essa
# igualdade (via == / !=) para conferir operandos e argumentos.

@dataclass(frozen=True)
class TNum:
    def __repr__(self):
        return "Num"

@dataclass(frozen=True)
class TBool:
    def __repr__(self):
        return "Bool"

@dataclass(frozen=True)
class TFun:
    params: tuple["Tipo", ...]   # (τ₁, …, τₙ)
    ret: "Tipo"                  # τ

    def __repr__(self):
        # a lista de parâmetros é sempre parentesada, mesmo vazia: () -> τ
        params = ", ".join(repr(t) for t in self.params)
        return f"({params}) -> {self.ret}"

type Tipo = TNum | TBool | TFun

def monadic_error(func):
    def wrapper(tokens, *args, **kwargs):
        if isinstance(tokens, Erro):
            return tokens
        return func(tokens, *args, **kwargs)
    return wrapper

# --- Geradores e Funções Predicado ---

def match_type(*types: TokenType) -> Callable[[Optional[Token]], Optional[Token]]:
    """Retorna uma função que aceita um Token se seu tipo for um dos esperados."""
    def predicate(tok: Optional[Token]) -> Optional[Token]:
        if tok and tok.type in types:
            return tok
        return None
    return predicate

# Predicados para tokens individuais
LPAREN   = match_type(TokenType.LPAREN)
RPAREN   = match_type(TokenType.RPAREN)
INTEIRO  = match_type(TokenType.INTEIRO)
POW      = match_type(TokenType.POW)
NOME     = match_type(TokenType.NOME)
LET      = match_type(TokenType.LET)
IN       = match_type(TokenType.IN)
EQUAL    = match_type(TokenType.EQUAL)
# aljabr v2 (§1): predicados das novas categorias
FN       = match_type(TokenType.FN)
ARROW    = match_type(TokenType.ARROW)
COMMA    = match_type(TokenType.COMMA)

# aljabr v3 (§1): predicados das novas categorias
LETREC   = match_type(TokenType.LETREC)
IF        = match_type(TokenType.IF)
THEN      = match_type(TokenType.THEN)
ELSE      = match_type(TokenType.ELSE)
EQEQ      = match_type(TokenType.EQEQ)
LT        = match_type(TokenType.LT)

# church v1 (§4.1): predicados das novas categorias
COLON      = match_type(TokenType.COLON)
TARROW     = match_type(TokenType.TARROW)
TNUM       = match_type(TokenType.TNUM)
TBOOL      = match_type(TokenType.TBOOL)
VERDADEIRO = match_type(TokenType.VERDADEIRO)
FALSO      = match_type(TokenType.FALSO)

# Predicados para grupos de operadores
OPERADOR = match_type(
    TokenType.ADD, TokenType.SUB, TokenType.MULT,
    TokenType.DIV, TokenType.POW
)
OPS_ADIT = match_type(TokenType.ADD, TokenType.SUB)
OPS_MULT = match_type(TokenType.MULT, TokenType.DIV)
UNARIO = match_type(TokenType.ADD, TokenType.SUB)


class Stream:
    def __init__(self, tokens: list[Token]):
        self.it = iter(tokens)

    def peek(self) -> Optional[Token]:
        try:
            valor = next(self.it)
        except StopIteration:
            return None
        self.it = chain((valor,), self.it)
        return valor

    def next(self) -> Optional[Token]:
        try:
            valor = next(self.it)
        except StopIteration:
            return None
        return valor

    def __iter__(self):
        return self.it
