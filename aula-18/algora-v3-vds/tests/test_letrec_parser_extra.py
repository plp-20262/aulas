import pytest

from lexer import tokenizador
from parser import parser
from tipos import FunDecl, Erro

def test_parser_def_sem_parametros():
    ast = parser(tokenizador("def f() { 1 } f()"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.stmts[0], FunDecl)
    assert ast.stmts[0].name == "f"
    assert ast.stmts[0].params == []

def test_parser_def_preserva_a_ordem_dos_parametros():
    ast = parser(tokenizador("def f(c, a, b) { a } f(1, 2, 3)"))
    assert not isinstance(ast, Erro)
    assert ast.stmts[0].params == ["c", "a", "b"]

def test_parser_def_com_um_parametro_e_muitos_parametros():
    ast = parser(tokenizador("def f(x) { x } def g(a, b, c, d, e) { a } 0"))
    assert not isinstance(ast, Erro)
    assert ast.stmts[0].params == ["x"]
    assert ast.stmts[1].params == ["a", "b", "c", "d", "e"]

def test_parser_def_corpo_com_comandos():
    ast = parser(tokenizador("def f(x) { var y := x; y := y + 1; y } f(1)"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.stmts[0], FunDecl)

def test_parser_def_aninhado():
    ast = parser(tokenizador("def f() { def g() { 1 } g() } f()"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.stmts[0], FunDecl)
    assert ast.stmts[0].name == "f"

def test_parser_def_dentro_de_bloco_fn_e_if():
    for code in ["{ def f() { 1 } f() }",
                 "if 1 { def f() { 1 } f() } else { 0 }",
                 "fn () { def f() { 1 } f() }"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code

def test_parser_def_com_nome_parecido_com_reservada():
    ast = parser(tokenizador("def iffy() { 1 } def Var() { 2 } def _() { 3 } iffy()"))
    assert not isinstance(ast, Erro)
    assert [s.name for s in ast.stmts] == ["iffy", "Var", "_"]

def test_parser_def_dois_com_mesmo_nome_e_sintaticamente_valido():
    ast = parser(tokenizador("def f() { 1 } def f() { 2 } f()"))
    assert not isinstance(ast, Erro)
    assert len(ast.stmts) == 2

REJEITADOS = [
    # parâmetros inválidos
    "def f(a,) { 1 } 1", "def f(,a) { 1 } 1", "def f(a b) { 1 } 1", "def f(a, , b) { 1 } 1",
    "def f(1) { 1 } 1", "def f(a, 1) { 1 } 1", "def f(a + 1) { 1 } 1",
    "def f(if) { 1 } 1", "def f(a, fn) { 1 } 1", "def f(var) { 1 } 1",
    # forma geral
    "def f { 1 } 1", "def f() 1 1", "def f(x) x + 1 1", "def (x) { 1 } 1",
    "def 1() { 1 } 1", "def if() { 1 } 1", "def def() { 1 } 1", "def var() { 1 } 1", "def else() { 1 } 1",
    "def f() { } 1", "def f() { var x := 1; } 1", "def f() { x := 1; } 1",
    "def f() = { 1 } 1", "def f() := { 1 } 1",
    # def não é expressão
    "(def f() { 1 })", "f(def g() { 1 })", "1 + def f() { 1 } 1", "var x := def f() { 1 }; 1",
    "if def f() { 1 } { 2 } else { 3 }", "x := def f() { 1 }; 1",
    # truncados / sem expressão final
    "def", "def f", "def f(", "def f(x", "def f(x,", "def f(x)", "def f(x) {", "def f(x) { x",
    "def f() { 1 }", "def f() { 1 } def g() { 2 }",
]

@pytest.mark.parametrize("code", REJEITADOS)
def test_parser_def_malformado_erro(code):
    ast = parser(tokenizador(code))
    assert isinstance(ast, Erro), code
