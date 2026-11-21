from lexer import tokenizador
from algora import executar_programa
from tipos import TokenType, Erro

# Testes de lexer dos novos terminais da versão v3 de Algora:
# `COLON` (`:`), `DOT` (`.`) e a palavra reservada `THIS` (`this`).
#
# Fundamento: README.md §1 (Léxico):
#
#     COLON     ::=  :              ← NOVO (v3)
#     DOT       ::=  \.             ← NOVO (v3)
#     THIS      ::=  this           ← NOVO (v3) (palavra reservada)
#
# Regras-chave observadas:
# - `:=` (`ASSIGN`) deve vir antes de `:` (`COLON`) e de `=` (`EQUAL`).
# - `.` é tokenizado como `DOT`.
# - `this` é palavra reservada (`TokenType.THIS`), sensível a maiúsculas;
#   identificadores que apenas contêm `this` (ex.: `thisx`, `This`) são `NOME`.


def _tipos(code: str) -> list[TokenType]:
    tokens = tokenizador(code)
    assert not isinstance(tokens, Erro), code
    return [t.type for t in tokens]


def test_lexer_novos_simbolos_colon_e_dot():
    tokens = tokenizador(": .")
    assert not isinstance(tokens, Erro)
    assert [t.type for t in tokens] == [TokenType.COLON, TokenType.DOT]
    assert [t.lexema for t in tokens] == [":", "."]


def test_lexer_assign_antes_de_colon_e_equal():
    # Maximal munch: `:=` deve ser reconhecido como ASSIGN, não COLON + EQUAL.
    assert _tipos(":=") == [TokenType.ASSIGN]
    assert _tipos("::=") == [TokenType.COLON, TokenType.ASSIGN]
    assert _tipos(":=:") == [TokenType.ASSIGN, TokenType.COLON]
    assert _tipos(": =") == [TokenType.COLON, TokenType.EQUAL]
    assert _tipos("::") == [TokenType.COLON, TokenType.COLON]


def test_lexer_dot_em_acesso_a_campo_e_encadeamento():
    assert _tipos("a.b.c") == [
        TokenType.NOME, TokenType.DOT, TokenType.NOME, TokenType.DOT, TokenType.NOME
    ]
    assert _tipos("this.n := 0;") == [
        TokenType.THIS, TokenType.DOT, TokenType.NOME,
        TokenType.ASSIGN, TokenType.INTEIRO, TokenType.SEMICOLON
    ]


def test_lexer_record_literal_tokens():
    assert _tipos("{ x: 1, y: 2 }") == [
        TokenType.LBRACE,
        TokenType.NOME, TokenType.COLON, TokenType.INTEIRO, TokenType.COMMA,
        TokenType.NOME, TokenType.COLON, TokenType.INTEIRO,
        TokenType.RBRACE,
    ]


def test_lexer_this_eh_palavra_reservada():
    tokens = tokenizador("this")
    assert not isinstance(tokens, Erro)
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.THIS
    assert tokens[0].lexema == "this"


def test_lexer_todas_as_palavras_reservadas_v3():
    tokens = tokenizador("var def fn if else while this")
    assert not isinstance(tokens, Erro)
    assert [t.type for t in tokens] == [
        TokenType.VAR, TokenType.FUNCTION, TokenType.FN,
        TokenType.IF, TokenType.ELSE, TokenType.WHILE, TokenType.THIS,
    ]


def test_lexer_this_case_sensitive_e_prefixos_sao_nomes():
    for nome in ["This", "THIS", "thisx", "this_1", "_this", "my_this"]:
        tokens = tokenizador(nome)
        assert not isinstance(tokens, Erro), nome
        assert len(tokens) == 1, nome
        assert tokens[0].type == TokenType.NOME, nome
        assert tokens[0].lexema == nome, nome


def test_lexer_this_nao_pode_ser_nome_de_funcao_nem_de_campo():
    # Embora `this` possa ser variável (`var this := ...`), por ser `THIS` e não
    # `NOME`, é rejeitado onde a gramática exige `NOME` (nome de função ou campo).
    for prog in ["def this() { 1 } 1", "{ this: 1 }", "var p := {}; p.this"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog
