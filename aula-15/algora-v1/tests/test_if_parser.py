from lexer import tokenizador
from parser import parser
from tipos import IfExpr, Erro

def test_parser_if_estilo_algora():
    ast = parser(tokenizador("if x < 10 { 1 } else { 2 }"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.final_expr, IfExpr)

def test_parser_if_sem_else_erro():
    ast = parser(tokenizador("if x { 1 }"))
    assert isinstance(ast, Erro)
    assert "esperava 'else'" in ast.msg
