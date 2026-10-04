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
    INPUT = auto()
    LPAREN = auto()
    RPAREN = auto()

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
INPUT    = match_type(TokenType.INPUT)

# Predicados para grupos de operadores
OPERADOR = match_type(
    TokenType.ADD, TokenType.SUB, TokenType.MULT, 
    TokenType.DIV, TokenType.POW, TokenType.INPUT
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
