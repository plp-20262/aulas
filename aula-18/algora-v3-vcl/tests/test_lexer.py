from lexer import tokenizador
from tipos import TokenType, Erro

def test_lexer_tokens_basicos():
    code = "var x := 10 + 20 * 3;"
    tokens = tokenizador(code)
    assert not isinstance(tokens, Erro)
    
    tipos = [t.type for t in tokens]
    assert tipos == [
        TokenType.VAR, TokenType.NOME, TokenType.ASSIGN,
        TokenType.INTEIRO, TokenType.ADD, TokenType.INTEIRO,
        TokenType.MULT, TokenType.INTEIRO, TokenType.SEMICOLON
    ]

def test_lexer_maiusculas_e_camelcase():
    code = "var criaContador := 10;"
    tokens = tokenizador(code)
    assert not isinstance(tokens, Erro)
    assert tokens[1].lexema == "criaContador"
    assert tokens[1].type == TokenType.NOME

def test_lexer_prioridade_operadores():
    code = ":= == ="
    tokens = tokenizador(code)
    assert not isinstance(tokens, Erro)
    assert tokens[0].type == TokenType.ASSIGN
    assert tokens[1].type == TokenType.EQEQ
    assert tokens[2].type == TokenType.EQUAL

def test_lexer_palavras_reservadas():
    code = "var def fn if else"
    tokens = tokenizador(code)
    assert not isinstance(tokens, Erro)
    assert [t.type for t in tokens] == [
        TokenType.VAR, TokenType.FUNCTION, TokenType.FN, TokenType.IF, TokenType.ELSE
    ]

def test_lexer_erro_mismatch():
    tokens = tokenizador("var x := 10 @ 20;")
    assert isinstance(tokens, Erro)
    assert "token desconhecido" in tokens.msg
