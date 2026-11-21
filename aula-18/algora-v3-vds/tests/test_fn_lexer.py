from lexer import tokenizador
from tipos import TokenType

def test_lexer_fn_e_function():
    tokens = tokenizador("def f(x) { fn () { x } }")
    tipos = [t.type for t in tokens]
    assert TokenType.FUNCTION in tipos
    assert TokenType.FN in tipos
    assert TokenType.LBRACE in tipos
    assert TokenType.RBRACE in tipos
