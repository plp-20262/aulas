from lexer import tokenizador
from parser import parser
from tipos import Block, VarDecl, Assign, FunDecl, ExprStmt, Num, Var, BinaryOp, Call, Erro

def test_parse_programa_simples():
    code = "var x := 10; x + 5"
    tokens = tokenizador(code)
    ast = parser(tokens)
    assert not isinstance(ast, Erro)
    assert isinstance(ast, Block)
    assert len(ast.stmts) == 1
    assert isinstance(ast.stmts[0], VarDecl)
    assert isinstance(ast.final_expr, BinaryOp)

def test_parse_funcao_nomeada():
    code = "def soma(a, b) { a + b } soma(2, 3)"
    tokens = tokenizador(code)
    ast = parser(tokens)
    assert not isinstance(ast, Erro)
    assert isinstance(ast.stmts[0], FunDecl)
    assert ast.stmts[0].name == "soma"
    assert ast.stmts[0].params == ["a", "b"]

def test_parse_expressao_como_comando():
    code = "f(); g(); 42"
    tokens = tokenizador(code)
    ast = parser(tokens)
    assert not isinstance(ast, Erro)
    assert len(ast.stmts) == 2
    assert isinstance(ast.stmts[0], ExprStmt)
    assert isinstance(ast.stmts[1], ExprStmt)
    assert isinstance(ast.final_expr, Num)
    assert ast.final_expr.value == 42

def test_parse_erro_tokens_sobrando():
    code = "1 + 2; 3 4"
    tokens = tokenizador(code)
    ast = parser(tokens)
    assert isinstance(ast, Erro)
    assert "tokens não consumidos" in ast.msg
