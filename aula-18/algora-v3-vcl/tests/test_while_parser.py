import pytest

from lexer import tokenizador
from parser import parser
from tipos import Erro

# Testes de parser (sintaxe) do comando `while` (versão v2 de Algora).
#
# Fundamento: README.md §2 (Sintaxe EBNF), seção v2:
#
#     while_cmd   ::= while exp bloco_cmd                    ← NOVO (v2)
#     bloco_cmd   ::= LBRACE { comando } RBRACE              ← NOVO (v2)
#
# Regras-chave observadas (caixa-preta, sem ler a implementação):
# - `while_cmd` é um comando e NÃO leva `;` depois (como `func_decl`).
# - Depois de `while ... { }`, o próximo comando/expressão começa logo a seguir,
#   sem `;` separador.
# - O corpo é um `bloco_cmd`: sequência de comandos sem expressão final, de modo
#   que toda expressão no corpo precisa terminar com `;`; um `while` interno no
#   corpo também não leva `;`.
# - Todo bloco `{ ... }` (incluindo ramos de `if` e corpos de função) exige uma
#   expressão final.
# - Um `while_cmd` não pode ser a última coisa de um `bloco_corpo`: precisa ser
#   seguido pela expressão final do bloco (programas terminam em expressão).
# - `while` é comando, não expressão: não pode aparecer onde se espera `exp`
#   (ex.: `var x := while ...` é inválido).


# ---------------- Programas sintaticamente válidos ----------------


def test_parser_while_falso_seguido_de_expressao_final():
    ast = parser(tokenizador("while 0 { } 1"))
    assert not isinstance(ast, Erro), "while 0 { } 1"


def test_parser_while_corpo_vazio():
    ast = parser(tokenizador("var i := 0; while i < 0 { } i"))
    assert not isinstance(ast, Erro), "corpo vazio é válido"


def test_parser_while_corpo_com_varios_comandos():
    ast = parser(tokenizador("var i := 0; while i < 3 { i := i + 1; } i"))
    assert not isinstance(ast, Erro), "cada comando do corpo termina em ;"


def test_parser_while_condicao_entre_parenteses():
    ast = parser(tokenizador("var i := 0; while (i < 2) { i := i + 1; } i"))
    assert not isinstance(ast, Erro), "condição pode estar entre parênteses"


def test_parser_while_condicao_eh_bloco():
    ast = parser(tokenizador("var i := 0; while { i < 2 } { i := i + 1; } i"))
    assert not isinstance(ast, Erro), "bloco é um atomo, logo pode ser condição"


def test_parser_while_condicao_eh_chamada():
    ast = parser(tokenizador("var i := 0; while i < 3 { i := i + 1; } i"))
    assert not isinstance(ast, Erro), "chamada é uma expressão, logo pode ser condição"


def test_parser_while_aninhado():
    ast = parser(tokenizador("var i := 0; var j := 0; while i < 2 { j := 0; while j < 3 { j := j + 1; } i := i + 1; } j"))
    assert not isinstance(ast, Erro), "while dentro de while"


def test_parser_while_dentro_de_if():
    ast = parser(tokenizador("if 1 { while 0 { } 1 } else { 2 }"))
    assert not isinstance(ast, Erro), "while_cmd é comando, pode ficar em ramo de if"


def test_parser_if_dentro_do_corpo_do_while():
    ast = parser(tokenizador("var i := 0; while i < 2 { if i == 0 { i := 1; 0 } else { i := 2; 0 }; } i"))
    assert not isinstance(ast, Erro), "if ; é comando válido no corpo do while (ramos são blocos com expressão final)"


def test_parser_def_dentro_do_corpo_do_while():
    ast = parser(tokenizador("var i := 0; while i < 1 { def f() { 1 } f(); i := i + 1; } i"))
    assert not isinstance(ast, Erro), "def é comando válido no corpo do while (sem ;)"


# ---------------- Programas sintaticamente inválidos ----------------


REJEITADOS = [
    # falta condição e corpo
    "while",
    # falta corpo (bloco_cmd)
    "while 1",
    # falta condição (exp)
    "while { }",
    # corpo não fechado
    "while 1 {",
    # corpo é bloco_cmd: expressão solta precisa de ; (2; seria válido)
    "while 1 { 2 }",
    # while_cmd não pode ser a expressão final do programa
    "while 0 { }",
    # while é comando, não expressão: não pode inicializar var
    "var x := while 0 { } 1",
    # while não aparece em exp
    "1 + while 0 { }",
    # x := 1 não é uma exp (atribuição é comando)
    "while x := 1 { }",
]


@pytest.mark.parametrize("code", REJEITADOS)
def test_parser_while_malformado_erro(code):
    ast = parser(tokenizador(code))
    assert isinstance(ast, Erro), repr(code)
