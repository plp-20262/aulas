from lexer import tokenizador
from parser import parser
from tipos import Block, VarDecl, Assign, ExprStmt, Num, Var, Erro

def test_parser_bloco_como_expressao_final():
    ast = parser(tokenizador("{ 1 }"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.final_expr, Block)
    assert isinstance(ast.final_expr.final_expr, Num)
    assert ast.final_expr.final_expr.value == 1

def test_parser_blocos_aninhados():
    ast = parser(tokenizador("{ { { 1 } } }"))
    assert not isinstance(ast, Erro)
    bloco1 = ast.final_expr
    bloco2 = bloco1.final_expr
    bloco3 = bloco2.final_expr
    assert isinstance(bloco1, Block)
    assert isinstance(bloco2, Block)
    assert isinstance(bloco3, Block)
    assert isinstance(bloco3.final_expr, Num)

def test_parser_bloco_com_comandos():
    ast = parser(tokenizador("{ var x := 1; x := 2; x }"))
    assert not isinstance(ast, Erro)
    bloco = ast.final_expr
    assert isinstance(bloco, Block)
    assert [type(s) for s in bloco.stmts] == [VarDecl, Assign]
    assert isinstance(bloco.final_expr, Var)

def test_parser_bloco_como_comando_com_ponto_e_virgula():
    ast = parser(tokenizador("{ x := 1; 0 }; 5"))
    assert not isinstance(ast, Erro)
    assert len(ast.stmts) == 1
    assert isinstance(ast.stmts[0], ExprStmt)
    assert isinstance(ast.final_expr, Num)

def test_parser_bloco_como_comando_exige_ponto_e_virgula():
    # bloco é uma expressão: "exp ;" é o comando, então "{ 1 } 2" é inválido
    ast = parser(tokenizador("{ 1 } 2"))
    assert isinstance(ast, Erro)
    assert "tokens não consumidos" in ast.msg

def test_parser_bloco_como_operando():
    for code in ["1 + { 2 }", "{ 1 } + { 2 }", "-{ 3 }", "{ 2 } ** { 3 }", "{ 1 } < { 2 }",
                 "f({ 1 }, { 2 })", "{ f }(1)", "({ 1 })", "{ 1 }(2)",
                 "if { 1 } { 2 } else { 3 }"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code

def test_parser_bloco_vazio_erro():
    for code in ["{}", "{ }", "{\n}", "{ {} }"]:
        ast = parser(tokenizador(code))
        assert isinstance(ast, Erro), code

def test_parser_bloco_sem_expressao_final_erro():
    for code in ["{ var x := 1; }", "{ 1; }", "{ x := 1; }", "{ def f() { 1 } }", "{ 1; 2; }"]:
        ast = parser(tokenizador(code))
        assert isinstance(ast, Erro), code

def test_parser_bloco_nao_fechado_erro():
    for code in ["{", "{ 1", "{ 1;", "{ { 1 }", "1 + { 2"]:
        ast = parser(tokenizador(code))
        assert isinstance(ast, Erro), code

def test_parser_chave_sobrando_erro():
    for code in ["}", "1 }", "{ 1 } }", "} 1", "{ 1 } 2 }"]:
        ast = parser(tokenizador(code))
        assert isinstance(ast, Erro), code

def test_parser_bloco_com_duas_expressoes_finais_erro():
    for code in ["{ 1 2 }", "{ x y }", "{ 1; 2 3 }"]:
        ast = parser(tokenizador(code))
        assert isinstance(ast, Erro), code
