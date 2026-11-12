from lexer import tokenizador
from parser import parser
from tipos import VarDecl, Assign, Erro

def test_parser_var_decl():
    ast = parser(tokenizador("var x := 42; x"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.stmts[0], VarDecl)
    assert ast.stmts[0].name == "x"

def test_parser_assign():
    ast = parser(tokenizador("x := 10; x"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.stmts[0], Assign)
    assert ast.stmts[0].name == "x"

def test_parser_var_sem_ponto_e_virgula():
    ast = parser(tokenizador("var x := 42 x"))
    assert isinstance(ast, Erro)
    assert "esperava ';'" in ast.msg
