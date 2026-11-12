import pytest

from lexer import tokenizador
from parser import parser
from tipos import AnonFun, Call, Erro

def test_parser_fn_sem_parametros_e_com_varios():
    for code in ["fn () { 1 }", "fn (a) { a }", "fn (a, b, c) { a }", "fn(a,b){a}"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code
        assert isinstance(ast.final_expr, AnonFun), code

def test_parser_fn_corpo_com_comandos():
    code = "fn (x) { var y := x; y := y + 1; def g() { y } g() }"
    ast = parser(tokenizador(code))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.final_expr, AnonFun)

def test_parser_fn_aninhada():
    ast = parser(tokenizador("fn (a) { fn (b) { fn (c) { a } } }"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.final_expr, AnonFun)

def test_parser_chamada_de_funcao_anonima_exige_parenteses():
    ast = parser(tokenizador("(fn (x) { x })(1)"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.final_expr, Call)

    # fn é uma "exp" completa, e não um "atomo": não pode ser chamada diretamente
    ast = parser(tokenizador("fn (x) { x }(1)"))
    assert isinstance(ast, Erro)
    assert "tokens não consumidos" in ast.msg

def test_parser_chamada_encadeada_longa():
    ast = parser(tokenizador("f(1)(2, 3)()(4)"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.final_expr, Call)

def test_parser_chamada_com_argumentos_de_varias_formas():
    code = "f(1 + 2, g(3), fn (x) { x }, { 4 }, if 1 { 5 } else { 6 }, -7, (8))"
    ast = parser(tokenizador(code))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.final_expr, Call)

def test_parser_chamada_de_literal_e_sintaticamente_valida():
    # o erro de "chamar um número" é semântico, não sintático
    for code in ["1(2)", "(1 + 2)(3)", "x(1)(2)", "(1 < 2)(0)"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code

REJEITADOS = [
    # parâmetros inválidos
    "fn (x,) { x }", "fn (,x) { x }", "fn (x y) { x }", "fn (x, , y) { x }",
    "fn (1) { 1 }", "fn (x, 1) { 1 }", "fn (x + 1) { 1 }", "fn ((x)) { 1 }",
    "fn (if) { 1 }", "fn (var) { 1 }", "fn (else) { 1 }", "fn (fn) { 1 }", "fn (def) { 1 }",
    # forma geral
    "fn x { x }", "fn { 1 }", "fn () 1", "fn (x) x", "fn ()", "fn () { }", "fn () { var x := 1; }",
    "fn (x", "fn (x,", "fn (", "fn",
    # argumentos inválidos
    "f(1,)", "f(,1)", "f(1,,2)", "f(1 2)", "f(", "f(1", "f(1,", "f)", "f(1))", "f((1)",
    "f(var x := 1)", "f(x := 1)", "f(def g() { 1 })",
]

@pytest.mark.parametrize("code", REJEITADOS)
def test_parser_fn_e_chamada_malformados_erro(code):
    ast = parser(tokenizador(code))
    assert isinstance(ast, Erro), code
