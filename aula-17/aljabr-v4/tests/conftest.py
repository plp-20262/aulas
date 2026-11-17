import pytest
from tipos import Erro, Token, TokenType
from aljabr import Environment, eval
from lexer import tokenizador
from parser import parser


@pytest.fixture
def env() -> Environment:
    """Ambiente vazio padrão."""
    return {}


@pytest.fixture
def parse():
    """Parse source string to AST."""
    def _parse(code: str):
        tokens = tokenizador(code)
        if isinstance(tokens, Erro):
            return tokens
        return parser(tokens)
    return _parse


@pytest.fixture
def eval_ast():
    """Evaluate AST directly (bypass parser)."""
    return eval


def token(lexema: str) -> Token:
    """Create a Token from a lexeme string using the lexer. Test utility."""
    tokens = tokenizador(lexema)
    if isinstance(tokens, Erro) or len(tokens) != 1:
        raise ValueError(f"invalid single lexeme: {lexema!r}")
    return tokens[0]


def assert_error(result, msg_substring: str = None):
    """Assert result is Erro, optionally checking message contains substring."""
    assert isinstance(result, Erro), f"Expected Erro, got {result!r}"
    if msg_substring:
        assert msg_substring in result.msg, f"Erro message '{result.msg}' does not contain '{msg_substring}'"


def _flatten(lst):
    """Helper to recursively find Erro in nested lists."""
    for item in lst:
        if isinstance(item, Erro):
            yield item
        elif isinstance(item, list):
            yield from _flatten(item)


def assert_error_in_ast(ast):
    """Assert AST (possibly nested) contains at least one Erro."""
    assert isinstance(ast, list), f"Expected list AST, got {ast!r}"
    assert any(isinstance(x, Erro) for x in _flatten(ast)), f"Expected Erro in AST, got {ast!r}"


def parse_code(code: str):
    """Helper to tokenize and parse a string, returning AST or Erro."""
    res = tokenizador(code)
    if isinstance(res, Erro):
        return res
    return parser(res)


def run(code: str):
    """Tokeniza, parseia e avalia um programa-fonte em ambiente vazio.

    Devolve o valor resultante ou um Erro. Usado pelos testes ponta-a-ponta
    da tabela de programas da §4.4 do README (v2).
    """
    ast = parse_code(code)
    if isinstance(ast, Erro):
        return ast
    return eval(ast, {})