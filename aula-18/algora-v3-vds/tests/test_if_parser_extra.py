import pytest

from lexer import tokenizador
from parser import parser
from tipos import IfExpr, ExprStmt, Num, Erro

def test_parser_if_como_comando_com_ponto_e_virgula():
    ast = parser(tokenizador("if 1 { 2 } else { 3 }; 4"))
    assert not isinstance(ast, Erro)
    assert len(ast.stmts) == 1
    assert isinstance(ast.stmts[0], ExprStmt)
    assert isinstance(ast.final_expr, Num)

def test_parser_if_condicao_complexa():
    ast = parser(tokenizador("if a + 1 < f(2) * 3 { 1 } else { 2 }"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.final_expr, IfExpr)

def test_parser_if_condicao_bloco_if_ou_parenteses():
    for code in ["if { 1 } { 2 } else { 3 }",
                 "if { var t := 1; t } { 2 } else { 3 }",
                 "if if 1 { 0 } else { 1 } { 2 } else { 3 }",
                 "if (1) { 2 } else { 3 }",
                 "if (fn () { 1 })() { 2 } else { 3 }"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code
        assert isinstance(ast.final_expr, IfExpr), code

def test_parser_if_aninhado_dentro_dos_ramos():
    for code in ["if 1 { if 2 { 3 } else { 4 } } else { 5 }",
                 "if 1 { 2 } else { if 3 { 4 } else { 5 } }",
                 "if 1 { if 2 { 3 } else { 4 } } else { if 5 { 6 } else { 7 } }"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code
        assert isinstance(ast.final_expr, IfExpr), code

def test_parser_if_em_posicoes_de_exp():
    for code in ["f(if 1 { 2 } else { 3 })",
                 "var x := if 1 { 2 } else { 3 }; x",
                 "x := if 1 { 2 } else { 3 }; x",
                 "f(1, if 1 { 2 } else { 3 }, 4)",
                 "{ if 1 { 2 } else { 3 } }"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code

def test_parser_if_sem_else_mensagem():
    for code in ["if 1 { 2 }", "if 1 { 2 }; 3", "if 1 { 2 } 3", "if x { if y { 1 } else { 2 } }"]:
        ast = parser(tokenizador(code))
        assert isinstance(ast, Erro), code
        assert "esperava 'else'" in ast.msg, code

def test_parser_nao_existe_else_if():
    # else ::= "else" bloco  (o ramo else sempre é um bloco)
    ast = parser(tokenizador("if 0 { 1 } else if 1 { 2 } else { 3 }"))
    assert isinstance(ast, Erro)
    ast = parser(tokenizador("if 0 { 1 } else { if 1 { 2 } else { 3 } }"))
    assert not isinstance(ast, Erro)

REJEITADOS = [
    "if 1 { 2 } else 3", "if 1 { 2 } else (3)", "if 1 { 2 } else x",
    "if 1 2 else 3", "if 1 2 else { 3 }", "if 1 { 2 } 3 else { 4 }",
    "if { 1 } else { 2 }", "if else { 1 }", "if { 1 }",
    "if 1 { } else { 2 }", "if 1 { 2 } else { }",
    "if 1 { var x := 1; } else { 2 }", "if 1 { 2 } else { x := 1; }",
    "if 1 { 2 } else { 3 } else { 4 }",
    "else { 1 }", "1 else { 2 }", "{ 1 } else { 2 }",
    "if", "if 1", "if 1 {", "if 1 { 2", "if 1 { 2 } else", "if 1 { 2 } else {", "if 1 { 2 } else { 3",
]

@pytest.mark.parametrize("code", REJEITADOS)
def test_parser_if_malformado_erro(code):
    ast = parser(tokenizador(code))
    assert isinstance(ast, Erro), code
