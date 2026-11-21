import pytest

from lexer import tokenizador
from tipos import TokenType, Erro

CARACTERES_FORA_DA_LINGUAGEM = [
    "@", "$", "%", "&", "!", "?", "[", "]", "|", "^", "~", ".", "'", "`", "\\", ":", ">",
]

@pytest.mark.parametrize("c", CARACTERES_FORA_DA_LINGUAGEM)
def test_lexer_caractere_fora_da_linguagem(c):
    tokens = tokenizador(f"var x := 1 {c} 2;")
    assert isinstance(tokens, Erro), c
    assert "token desconhecido" in tokens.msg

def test_lexer_erro_em_qualquer_posicao():
    # o resultado é um Erro (e não uma lista parcial de tokens)
    for code in ["@", "@ 1", "1 @ 2", "1 @", "1 + 2 + 3 + 4 @"]:
        tokens = tokenizador(code)
        assert isinstance(tokens, Erro), code
        assert "token desconhecido" in tokens.msg

def test_lexer_nao_ha_numeros_decimais():
    for code in ["1.5", ".5", "1.", "0.0", "var x := 3.14;"]:
        tokens = tokenizador(code)
        assert isinstance(tokens, Erro), code
        assert "token desconhecido" in tokens.msg

def test_lexer_nao_ha_operadores_extras():
    for code in ["a != b", "a >= b", "a > b", "a && b", "a || b", "a % b", "a -> b"]:
        tokens = tokenizador(code)
        assert isinstance(tokens, Erro), code
        assert "token desconhecido" in tokens.msg

def test_lexer_dois_pontos_isolado_nao_e_atribuicao():
    for code in [":", "x : 1", "x :", "x =: 1"]:
        tokens = tokenizador(code)
        assert isinstance(tokens, Erro), code
        assert "token desconhecido" in tokens.msg

def test_lexer_letras_acentuadas_nao_formam_nome():
    # NOME ::= [a-zA-Z_][a-zA-Z0-9_]*  (somente ASCII)
    for code in ["var ação := 1;", "é", "x_ç", "ñ = 1", "naïve"]:
        tokens = tokenizador(code)
        assert isinstance(tokens, Erro), code
        assert "token desconhecido" in tokens.msg

def test_lexer_digitos_nao_ascii_nao_formam_inteiro():
    # INTEIRO ::= [0-9]+  (somente ASCII)
    for code in ["٣", "١٢٣", "²"]:
        tokens = tokenizador(code)
        assert isinstance(tokens, Erro), code

def test_lexer_aspas_nao_formam_strings():
    for code in ['"abc"', '"', 'var s := "oi";']:
        tokens = tokenizador(code)
        assert isinstance(tokens, Erro), code
        assert "token desconhecido" in tokens.msg

def test_lexer_sem_erro_antes_do_primeiro_caractere_invalido():
    # o trecho válido isolado tokeniza normalmente
    tokens = tokenizador("var x := 10 ")
    assert not isinstance(tokens, Erro)
    assert tokens[-1].type == TokenType.INTEIRO
