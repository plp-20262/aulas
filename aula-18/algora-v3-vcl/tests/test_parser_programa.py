from lexer import tokenizador
from parser import parser
from tipos import Block, VarDecl, Assign, FunDecl, ExprStmt, Num, Call, Erro

def test_parser_programa_so_com_expressao_final():
    ast = parser(tokenizador("42"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast, Block)
    assert len(ast.stmts) == 0
    assert isinstance(ast.final_expr, Num)
    assert ast.final_expr.value == 42

def test_parser_inteiro_com_zeros_a_esquerda():
    ast = parser(tokenizador("007"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.final_expr, Num)
    assert ast.final_expr.value == 7

def test_parser_sequencia_com_todos_os_tipos_de_comando():
    ast = parser(tokenizador("var x := 1; x := 2; f(); def g() { 1 } g()"))
    assert not isinstance(ast, Erro)
    assert [type(s) for s in ast.stmts] == [VarDecl, Assign, ExprStmt, FunDecl]
    assert isinstance(ast.final_expr, Call)

def test_parser_ordem_dos_comandos_e_preservada():
    ast = parser(tokenizador("var a := 1; var b := 2; var c := 3; a"))
    assert not isinstance(ast, Erro)
    assert [s.name for s in ast.stmts] == ["a", "b", "c"]

def test_parser_varios_comandos_de_expressao():
    ast = parser(tokenizador("1; 2; 3; 4"))
    assert not isinstance(ast, Erro)
    assert len(ast.stmts) == 3
    assert all(isinstance(s, ExprStmt) for s in ast.stmts)
    assert isinstance(ast.final_expr, Num)
    assert ast.final_expr.value == 4

def test_parser_formas_variadas_de_expressao_como_comando():
    code = "x; (y); { 1 }; fn () { 1 }; if 1 { 2 } else { 3 }; f(1)(2); -z; 0"
    ast = parser(tokenizador(code))
    assert not isinstance(ast, Erro)
    assert len(ast.stmts) == 7
    assert all(isinstance(s, ExprStmt) for s in ast.stmts)
    assert isinstance(ast.final_expr, Num)

def test_parser_def_nao_exige_ponto_e_virgula():
    ast = parser(tokenizador("def f() { 1 } def g() { 2 } f() + g()"))
    assert not isinstance(ast, Erro)
    assert [type(s) for s in ast.stmts] == [FunDecl, FunDecl]
    assert [s.name for s in ast.stmts] == ["f", "g"]

def test_parser_expressao_apos_def_nao_vira_chamada():
    # "def" é um comando completo ao fechar a chave: o que vem depois é nova expressão
    ast = parser(tokenizador("def f() { 1 } (2)"))
    assert not isinstance(ast, Erro)
    assert len(ast.stmts) == 1
    assert not isinstance(ast.final_expr, Call)

    ast = parser(tokenizador("def f() { 1 } -3"))
    assert not isinstance(ast, Erro)
    assert len(ast.stmts) == 1

def test_parser_def_seguido_de_ponto_e_virgula_erro():
    # comando ::= func_decl  (sem ";" e sem comando vazio na gramática)
    ast = parser(tokenizador("def f() { 1 }; f()"))
    assert isinstance(ast, Erro)

def test_parser_programa_vazio_erro():
    for code in ["", "   ", "\n\n"]:
        ast = parser(tokenizador(code))
        assert isinstance(ast, Erro), repr(code)

def test_parser_programa_sem_expressao_final_erro():
    for code in ["var x := 1;", "x := 1;", "1;", "def f() { 1 }",
                 "var x := 1; def f() { 2 }", "1; 2; 3;"]:
        ast = parser(tokenizador(code))
        assert isinstance(ast, Erro), code

def test_parser_ponto_e_virgula_solto_erro():
    for code in [";", "; 1", "1;; 2", "var x := 1;; x", "1; ; 2"]:
        ast = parser(tokenizador(code))
        assert isinstance(ast, Erro), code

def test_parser_expressao_final_nao_aceita_ponto_e_virgula_no_fim_sem_nova_expressao():
    ast = parser(tokenizador("var x := 1; x;"))
    assert isinstance(ast, Erro)

def test_parser_tokens_sobrando_mensagem():
    for code in ["1 2", "x y", "1 }", "1 )", "(1) 2", "1 < 2 < 3", "1 == 2 == 3", "1 < 2 == 3"]:
        ast = parser(tokenizador(code))
        assert isinstance(ast, Erro), code
        assert "tokens não consumidos" in ast.msg, code
