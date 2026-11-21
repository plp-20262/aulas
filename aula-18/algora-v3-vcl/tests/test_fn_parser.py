from lexer import tokenizador
from parser import parser
from tipos import AnonFun, Call, FunDecl, Erro

def test_parser_function_decl():
    ast = parser(tokenizador("def add(a, b) { a + b } add(1, 2)"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.stmts[0], FunDecl)
    assert ast.stmts[0].name == "add"

def test_parser_anon_fn():
    ast = parser(tokenizador("fn (x) { x + 1 }"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.final_expr, AnonFun)
