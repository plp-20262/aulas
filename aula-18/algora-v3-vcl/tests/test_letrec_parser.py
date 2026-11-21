from lexer import tokenizador
from parser import parser
from tipos import FunDecl, Erro

def test_parser_funcao_recursiva():
    code = """
    def rec(x) {
        if x == 0 { 0 } else { rec(x - 1) }
    }
    rec(3)
    """
    ast = parser(tokenizador(code))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.stmts[0], FunDecl)
    assert ast.stmts[0].name == "rec"
