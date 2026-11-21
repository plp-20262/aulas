import pytest

from lexer import tokenizador
from parser import parser
from tipos import (
    Block, VarDecl, Assign, FunDecl, ExprStmt, While, FieldWrite,
    Num, Var, AnonFun, Call, BinaryOp, UnaryOp, IfExpr, RecordLit, FieldRead,
    Erro
)

# Testes de parser (sintaxe) de records e `this` (versão v3 de Algora).
#
# Fundamento: README.md §2 (Sintaxe EBNF) e §2.1 (Notas sobre a sintaxe):
#
#     var_decl    ::= var var_name := exp
#     atribuicao  ::= var_name := exp
#                   | chamada DOT NOME := exp            ← NOVO (v3)
#     var_name    ::= NOME | THIS                        ← NOVO (v3)
#     params      ::= var_name { , var_name }            ← NOVO (v3)
#     chamada     ::= atomo { sufixo }
#     sufixo      ::= DOT NOME                           ← NOVO (v3)
#                   | LPAREN [ args ] RPAREN
#     atomo       ::= INTEIRO | NOME | THIS
#                   | LPAREN exp RPAREN | bloco | record_lit
#     record_lit  ::= LBRACE [ campos ] RBRACE           ← NOVO (v3)
#     campos      ::= campo { , campo }
#     campo       ::= NOME COLON exp


# ---------------- Literais de record e desambiguação de '{' ----------------


def test_parser_record_vazio():
    for code in ["{}", "{ }", "{\n}"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code
        assert isinstance(ast.final_expr, RecordLit), code
        assert ast.final_expr.fields == [], code


def test_parser_record_um_e_varios_campos():
    ast = parser(tokenizador("{ x: 1 }"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.final_expr, RecordLit)
    assert ast.final_expr.fields == [("x", Num(1))]

    ast = parser(tokenizador("{ x: 1, y: 2, z: 3 }"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.final_expr, RecordLit)
    assert [k for k, _ in ast.final_expr.fields] == ["x", "y", "z"]


def test_parser_record_campos_com_expressoes_variadas():
    code = "{ a: 1 + 2, b: fn (x) { x }, c: if 1 { 2 } else { 3 }, d: { k: 4 }, e: { var t := 5; t } }"
    ast = parser(tokenizador(code))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.final_expr, RecordLit)
    assert [k for k, _ in ast.final_expr.fields] == ["a", "b", "c", "d", "e"]
    assert isinstance(ast.final_expr.fields[3][1], RecordLit)
    assert isinstance(ast.final_expr.fields[4][1], Block)


def test_parser_desambiguacao_bloco_vs_record():
    # `{ x }` e `{ x + 1 }` e `{ x; 1 }` são blocos, não records
    for code in ["{ x }", "{ x + 1 }", "{ x; 1 }", "{ var x := 1; x }", "{ x := 1; x }"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code
        assert isinstance(ast.final_expr, Block), code

    # `{ {} }` e `{ { x: 1 } }`: bloco externo contendo record interno
    for code in ["{ {} }", "{ { x: 1 } }"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code
        assert isinstance(ast.final_expr, Block), code
        assert isinstance(ast.final_expr.final_expr, RecordLit), code


def test_parser_funcao_retornando_record_com_chaves_duplas():
    # README §2.1: corpo de função é `bloco`; chaves duplas retornam um record
    ast = parser(tokenizador("def ponto(x, y) { { x: x, y: y } } ponto(1, 2)"))
    assert not isinstance(ast, Erro)
    fn_decl = ast.stmts[0]
    assert isinstance(fn_decl, FunDecl)
    assert isinstance(fn_decl.body, Block)
    assert isinstance(fn_decl.body.final_expr, RecordLit)


# ---------------- Acesso a campo e encadeamento em `chamada` ----------------


def test_parser_acesso_a_campo_simples_e_encadeado():
    ast = parser(tokenizador("p.x"))
    assert not isinstance(ast, Erro)
    assert ast.final_expr == FieldRead(Var("p"), "x")

    ast = parser(tokenizador("a.b.c"))
    assert not isinstance(ast, Erro)
    assert ast.final_expr == FieldRead(FieldRead(Var("a"), "b"), "c")


def test_parser_chamada_de_metodo_canonica_e_direta():
    # README §2.1: `obj.m(args)` e `(obj.m)(args)` produzem a mesma AST
    ast1 = parser(tokenizador("obj.m(1, 2)"))
    ast2 = parser(tokenizador("(obj.m)(1, 2)"))
    assert not isinstance(ast1, Erro)
    assert not isinstance(ast2, Erro)
    assert ast1.final_expr == ast2.final_expr
    assert ast1.final_expr == Call(FieldRead(Var("obj"), "m"), [Num(1), Num(2)])


def test_parser_encadeamento_livre_de_campos_e_chamadas():
    for code in ["a.b(c).d(e)", "f().x", "f(1).g(2).h", "{ x: 1 }.x", "(p).x"]:
        ast = parser(tokenizador(code))
        assert not isinstance(ast, Erro), code


def test_parser_precedencia_de_dot_sobre_unario_e_potencia():
    ast = parser(tokenizador("-p.x"))
    assert not isinstance(ast, Erro)
    assert ast.final_expr == UnaryOp("-", FieldRead(Var("p"), "x"))

    ast = parser(tokenizador("p.x ** 2"))
    assert not isinstance(ast, Erro)
    assert ast.final_expr == BinaryOp("**", FieldRead(Var("p"), "x"), Num(2))


# ---------------- Atribuição a campo (`FieldWrite`) ----------------


def test_parser_atribuicao_a_campo_simples_e_encadeada():
    ast = parser(tokenizador("p.x := 10; p.x"))
    assert not isinstance(ast, Erro)
    assert ast.stmts == [FieldWrite(Var("p"), "x", Num(10))]

    ast = parser(tokenizador("a.b.c := 5; a"))
    assert not isinstance(ast, Erro)
    assert ast.stmts == [FieldWrite(FieldRead(Var("a"), "b"), "c", Num(5))]

    ast = parser(tokenizador("f().x := 5; 0"))
    assert not isinstance(ast, Erro)
    assert ast.stmts == [FieldWrite(Call(Var("f"), []), "x", Num(5))]


def test_parser_atribuicao_a_campo_dentro_de_while():
    ast = parser(tokenizador("var p := { x: 0 }; while p.x < 3 { p.x := p.x + 1; } p.x"))
    assert not isinstance(ast, Erro)
    while_stmt = ast.stmts[1]
    assert isinstance(while_stmt, While)
    assert len(while_stmt.body) == 1
    assert isinstance(while_stmt.body[0], FieldWrite)


# ---------------- Palavra reservada `this` como `var_name` ----------------


def test_parser_this_em_var_assign_params_e_atomo():
    ast = parser(tokenizador("var this := {}; this.n := 0; this := { n: 1 }; this.n"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.stmts[0], VarDecl) and ast.stmts[0].name == "this"
    assert isinstance(ast.stmts[1], FieldWrite) and ast.stmts[1].obj == Var("this")
    assert isinstance(ast.stmts[2], Assign) and ast.stmts[2].name == "this"
    assert ast.final_expr == FieldRead(Var("this"), "n")

    ast = parser(tokenizador("def f(this, x) { this.n + x } fn (this) { this }"))
    assert not isinstance(ast, Erro)
    assert isinstance(ast.stmts[0], FunDecl)
    assert ast.stmts[0].params == ["this", "x"]
    assert isinstance(ast.final_expr, AnonFun)
    assert ast.final_expr.params == ["this"]


# ---------------- Programas sintaticamente inválidos ----------------


REJEITADOS = [
    # `this` não pode ser nome de função nem de campo
    "def this() { 1 } 1",
    "{ this: 1 }",
    "{ x: 1, this: 2 }",
    "p.this",
    "p.this := 1; 0",
    # nomes de campo inválidos ou record malformado
    "{ 1: 2 }",
    "{ (x): 1 }",
    "{ x: 1, }",
    "{ , x: 1 }",
    "{ x: }",
    "{ : 1 }",
    "{ x 1 }",
    "{ x := 1 }",
    # acesso a campo malformado
    "p.",
    "p..x",
    ".x",
    "p.1",
    "p.(x)",
    # atribuição a campo sem ';' ou em posição de expressão
    "p.x := 1",
    "var y := p.x := 1; y",
    "(p.x := 1)",
    "1 + p.x := 2; 0",
    "-p.x := 1; 0",
    # chamada de função sem `.NOME` final não é alvo de atribuição
    "f() := 1; 0",
    "p.m() := 1; 0",
    # corpos de função e ramos de `if` continuam exigindo `bloco` (não aceitam `{}` vazio)
    "def f() { } 1",
    "fn () { }",
    "if 1 { } else { 2 }",
    "if 1 { 2 } else { }",
]


@pytest.mark.parametrize("code", REJEITADOS)
def test_parser_records_malformados_erro(code):
    ast = parser(tokenizador(code))
    assert isinstance(ast, Erro), repr(code)
