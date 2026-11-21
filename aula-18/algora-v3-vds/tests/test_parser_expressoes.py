import pytest

from lexer import tokenizador
from parser import parser
from tipos import Block, Num, Var, BinaryOp, Call, IfExpr, AnonFun, Erro

EXPRESSOES_VALIDAS = [
    # átomos
    "1", "x", "(1)", "((1))", "(((x)))", "{ 1 }",
    # sinais (um único sinal por operando) e operadores binários
    "-1", "+1", "-x", "- (1)", "-(-1)", "-(-(-1))",
    "1 - -1", "1 + -1", "1 * -1", "1 / -1", "1 ** -1", "-2 ** -2",
    "1 -- 2", "1 ++ 2", "1 +- 2", "1 -+ 2", "1--2",
    "1 + 2 * 3 - 4 / 5", "2 ** 3 ** 4", "(1 + 2) ** (3 - 4)",
    "1 < 2", "1 == 2", "1 + 2 < 3 * 4", "1 + 2 == 3 + 4", "(1 < 2) == (3 < 4)", "(1 < 2) < 3",
    # chamadas
    "f()", "f(1)", "f(1, 2, 3)", "f(1)(2)", "f()()()", "f(1)(2)(3)", "(f)(1)", "{ f }(1)",
    "(fn () { 1 })()", "(fn (x) { x })(1)", "(fn (x) { fn (y) { x } })(1)(2)",
    "f(1 + 2, g(3), x * y)", "f(fn (x) { x }, 2)", "f({ 1 }, 2)", "f(if 1 { 2 } else { 3 })",
    "1(2)", "(1 + 2)(3)", "-f(1)", "f(1) ** 2", "f(1) + f(2) * f(3)",
    # fn e if como expressões completas
    "fn () { 1 }", "fn (a, b, c) { a }", "fn (x) { var y := x; y }",
    "if 1 { 2 } else { 3 }", "if x < 1 { f(1) } else { g(2) }",
    "(if 1 { 2 } else { 3 })", "1 + (if 1 { 2 } else { 3 })", "(fn () { 1 }) + 2",
    "if (1) { 2 } else { 3 }", "if f(1) { 2 } else { 3 }", "if { 1 } { 2 } else { 3 }",
    "if if 1 { 0 } else { 1 } { 2 } else { 3 }",
    "if 1 { 2 } else { if 3 { 4 } else { 5 } }",
    "if 1 { if 2 { 3 } else { 4 } } else { 5 }",
    # comandos
    "var x := 1; x", "var f := fn () { 1 }; f()", "var y := if 1 { 2 } else { 3 }; y",
    "var z := { 1 }; z", "x := 1; 2", "x := if 1 { 2 } else { 3 }; x",
    "1; 2; 3", "x; y; z", "(1); 2", "{ 1 }; 2", "{ 1 } + 2", "if 1 { 2 } else { 3 }; 4",
    "def f() { 1 } f()", "def f() { 1 } def g() { 2 } f() + g()", "def f(a, b) { a } -3",
]

@pytest.mark.parametrize("code", EXPRESSOES_VALIDAS)
def test_parser_aceita_expressao_valida(code):
    ast = parser(tokenizador(code))
    assert not isinstance(ast, Erro), ast
    assert isinstance(ast, Block)

def test_parser_expressoes_com_operador_binario():
    for code in ["1 + 2", "1 - 2", "1 * 2", "1 / 2", "2 ** 3", "(1 + 2) * 3", "1 + 2 * 3"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code
        assert isinstance(ast.final_expr, BinaryOp), code

def test_parser_expressao_variavel_e_numero():
    ast = parser(tokenizador("x"))
    assert isinstance(ast.final_expr, Var)
    ast = parser(tokenizador("(7)"))
    assert isinstance(ast.final_expr, Num)

def test_parser_chamadas_encadeadas():
    for code in ["f(1)(2)", "f()()", "(f)(1)", "(fn () { 1 })()", "f(1)(2)(3)(4)"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code
        assert isinstance(ast.final_expr, Call), code

def test_parser_if_e_fn_entre_parenteses_continuam_sendo_if_e_fn():
    ast = parser(tokenizador("(if 1 { 2 } else { 3 })"))
    assert isinstance(ast.final_expr, IfExpr)
    ast = parser(tokenizador("(fn () { 1 })"))
    assert isinstance(ast.final_expr, AnonFun)

def test_parser_chamada_de_bloco():
    ast = parser(tokenizador("{ f }(1)"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.final_expr, Call)

def test_parser_comparacao_nao_e_associativa():
    # comp ::= soma [ ( == | < ) soma ]  (no máximo um operador de comparação)
    for code in ["1 < 2 < 3", "1 == 1 == 1", "1 < 2 == 3", "1 == 2 < 3", "a < b < c"]:
        ast = parser(tokenizador(code))
        assert isinstance(ast, Erro), code

def test_parser_apenas_um_sinal_unario():
    # unario ::= [ + | - ] chamada
    for code in ["--1", "- - 1", "+-1", "-+1", "++1", "1 - - - 2", "- -x", "-(1) - - - 1"]:
        ast = parser(tokenizador(code))
        assert isinstance(ast, Erro), code

def test_parser_if_e_fn_nao_sao_operandos_sem_parenteses():
    # só "atomo" pode ser operando; if/fn são "exp" completas
    for code in ["1 + if 1 { 2 } else { 3 }", "1 + fn () { 1 }", "-if 1 { 1 } else { 2 }",
                 "2 ** if 1 { 1 } else { 2 }", "1 == if 1 { 1 } else { 1 }",
                 "if 1 { 1 } else { 2 } + 3", "fn () { 1 } + 2", "fn (x) { x }(1)",
                 "if 1 { fn () { 1 } } else { fn () { 2 } }(0)"]:
        ast = parser(tokenizador(code))
        assert isinstance(ast, Erro), code
