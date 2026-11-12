import pytest

from lexer import tokenizador
from parser import parser
from tipos import VarDecl, Assign, Erro

def test_parser_var_decl_com_expressao_complexa():
    ast = parser(tokenizador("var x := 1 + 2 * f(3) - (4 / 5); x"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.stmts[0], VarDecl)
    assert ast.stmts[0].name == "x"

def test_parser_var_decl_com_fn_if_e_bloco():
    for code in ["var f := fn (x) { x }; f", "var y := if 1 { 2 } else { 3 }; y", "var z := { 1 }; z"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code
        assert isinstance(ast.stmts[0], VarDecl), code

def test_parser_var_decl_com_nome_parecido_com_reservada():
    ast = parser(tokenizador("var iffy := 1; var Var := 2; var _ := 3; iffy"))
    assert not isinstance(ast, Erro)
    assert [s.name for s in ast.stmts] == ["iffy", "Var", "_"]

def test_parser_assign_com_expressao():
    for code in ["x := x + 1; x", "x := fn () { 1 }; x", "x := if 1 { 2 } else { 3 }; x", "x := { 1 }; x"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code
        assert isinstance(ast.stmts[0], Assign), code
        assert ast.stmts[0].name == "x", code

def test_parser_declaracoes_e_atribuicoes_intercaladas():
    ast = parser(tokenizador("var a := 1; a := 2; var b := a; b := b + a; b"))
    assert not isinstance(ast, Erro)
    assert [type(s) for s in ast.stmts] == [VarDecl, Assign, VarDecl, Assign]
    assert [s.name for s in ast.stmts] == ["a", "a", "b", "b"]

def test_parser_sem_ponto_e_virgula_mensagem():
    for code in ["var x := 1", "x := 1", "var x := 1 y", "x := 1 y", "var x := 1 var y := 2; y"]:
        ast = parser(tokenizador(code))
        assert isinstance(ast, Erro), code
        assert "esperava ';'" in ast.msg, code

REJEITADOS = [
    # atribuição não é expressão (não encadeia nem aparece dentro de exp)
    "x := y := 1; x", "var x := y := 1; x", "(x := 1)", "f(x := 1)", "1 + x := 2; 1",
    "if x := 1 { 1 } else { 2 }", "{ x := 1 }", "var x := 1; x := 2", "x := 1 := 2; 1",
    # alvo da atribuição precisa ser NOME
    "1 := 2; 1", "(x) := 1; 1", "f() := 1; 1", "x + 1 := 2; 1", "{ x } := 1; 1", "-x := 1; 1",
    "f(1) := 2; 1", "var x := 1; x() := 2; 1",
    # "=" simples não é atribuição nem declaração
    "var x = 1; x", "x = 1; x", "1 = 1", "var x := 1 = 2; x", "var x = 1", ":= 1", "x :=",
    # declaração malformada
    "var := 1; 1", "var 1 := 2; 1", "var x; x", "var x := ; x", "var x 1; x", "var; 1",
    "var f(x) := 1; 1", "var x y := 1; 1", "var var x := 1; 1", "var x := var y := 1; 1",
    # reservadas não são nomes
    "var var := 1; 1", "var def := 1; 1", "var fn := 1; 1", "var if := 1; 1", "var else := 1; 1",
    "if := 1; 1", "fn := 1; 1", "def := 1; 1", "else := 1; 1",
    "x := else; 1", "x := var; 1",
    # truncados
    "var", "var x", "var x :=", "var x := 1 +",
]

@pytest.mark.parametrize("code", REJEITADOS)
def test_parser_var_e_atribuicao_malformados_erro(code):
    ast = parser(tokenizador(code))
    assert isinstance(ast, Erro), code
