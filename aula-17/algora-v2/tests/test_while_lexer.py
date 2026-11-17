from algora import executar_programa
from tipos import Erro

# Testes de lexer da palavra reservada `while` (versão v2 de Algora).
#
# Fundamento: README.md §1 (Léxico) — `WHILE ::= while` é uma palavra
# reservada (`← NOVO (v2)`), portanto não pode ser usada como `NOME`.
#
# Convenção: `while` sozinho é um token reservado; identificadores que apenas
# começam com `while` (ex.: `whilex`, `While`) são nomes válidos, pois a
# correspondência de palavras reservadas é exata e sensível a maiúsculas.


def test_lexer_while_reservado_nao_pode_ser_nome_de_variavel():
    # `while` não entra na categoria NOME: `var while := ...` é rejeitado.
    res = executar_programa("var while := 1; while", {}, {})
    assert isinstance(res, Erro), "while não pode ser nome de variável"


def test_lexer_while_reservado_nao_pode_ser_nome_de_funcao():
    # `while` não pode ser nome de função declarada com `def`.
    res = executar_programa("def while() { 1 }", {}, {})
    assert isinstance(res, Erro), "while não pode ser nome de função"


def test_lexer_case_sensitive_While_e_nome_valido():
    # A correspondência de palavras reservadas é sensível a maiúsculas.
    assert executar_programa("var While := 7; While", {}, {}) == 7


def test_lexer_prefixo_whilex_e_nome_valido():
    # `whilex` não é a palavra reservada exata `while`.
    assert executar_programa("var whilex := 3; whilex", {}, {}) == 3
