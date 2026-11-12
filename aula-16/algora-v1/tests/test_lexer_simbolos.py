from lexer import tokenizador
from tipos import TokenType, Erro

def _tipos(code):
    tokens = tokenizador(code)
    assert not isinstance(tokens, Erro), code
    return [t.type for t in tokens]

def test_lexer_todos_os_simbolos():
    tokens = tokenizador(":= == = < ** + - * / ( ) { } ; ,")
    assert not isinstance(tokens, Erro)
    assert [t.type for t in tokens] == [
        TokenType.ASSIGN, TokenType.EQEQ, TokenType.EQUAL, TokenType.LT, TokenType.POW,
        TokenType.ADD, TokenType.SUB, TokenType.MULT, TokenType.DIV,
        TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE, TokenType.RBRACE,
        TokenType.SEMICOLON, TokenType.COMMA
    ]
    assert [t.lexema for t in tokens] == [
        ":=", "==", "=", "<", "**", "+", "-", "*", "/", "(", ")", "{", "}", ";", ","
    ]

def test_lexer_pow_antes_de_mult():
    assert _tipos("2**3") == [TokenType.INTEIRO, TokenType.POW, TokenType.INTEIRO]
    assert _tipos("2***3") == [TokenType.INTEIRO, TokenType.POW, TokenType.MULT, TokenType.INTEIRO]
    assert _tipos("2****3") == [TokenType.INTEIRO, TokenType.POW, TokenType.POW, TokenType.INTEIRO]
    assert _tipos("2 * * 3") == [TokenType.INTEIRO, TokenType.MULT, TokenType.MULT, TokenType.INTEIRO]
    assert _tipos("2*-3") == [TokenType.INTEIRO, TokenType.MULT, TokenType.SUB, TokenType.INTEIRO]

def test_lexer_eqeq_antes_de_equal():
    assert _tipos("===") == [TokenType.EQEQ, TokenType.EQUAL]
    assert _tipos("====") == [TokenType.EQEQ, TokenType.EQEQ]
    assert _tipos("= =") == [TokenType.EQUAL, TokenType.EQUAL]
    assert _tipos("x==y") == [TokenType.NOME, TokenType.EQEQ, TokenType.NOME]
    assert _tipos("x=y") == [TokenType.NOME, TokenType.EQUAL, TokenType.NOME]

def test_lexer_assign_antes_de_equal():
    assert _tipos(":==") == [TokenType.ASSIGN, TokenType.EQUAL]
    assert _tipos(":===") == [TokenType.ASSIGN, TokenType.EQEQ]
    assert _tipos(":=:=") == [TokenType.ASSIGN, TokenType.ASSIGN]
    assert _tipos("=:=") == [TokenType.EQUAL, TokenType.ASSIGN]
    assert _tipos(":= =") == [TokenType.ASSIGN, TokenType.EQUAL]
    assert _tipos("x:=y:=z") == [
        TokenType.NOME, TokenType.ASSIGN, TokenType.NOME, TokenType.ASSIGN, TokenType.NOME
    ]

def test_lexer_menor_que_nao_tem_menor_igual():
    # só existem "<" e "==": "<=" são dois tokens
    assert _tipos("<=") == [TokenType.LT, TokenType.EQUAL]
    assert _tipos("<<") == [TokenType.LT, TokenType.LT]
    assert _tipos("<==") == [TokenType.LT, TokenType.EQEQ]
    assert _tipos("a<b") == [TokenType.NOME, TokenType.LT, TokenType.NOME]

def test_lexer_nao_ha_literal_negativo():
    assert _tipos("-1") == [TokenType.SUB, TokenType.INTEIRO]
    assert _tipos("1-1") == [TokenType.INTEIRO, TokenType.SUB, TokenType.INTEIRO]
    assert _tipos("1--1") == [TokenType.INTEIRO, TokenType.SUB, TokenType.SUB, TokenType.INTEIRO]
    assert _tipos("x -1") == [TokenType.NOME, TokenType.SUB, TokenType.INTEIRO]
    assert _tipos("+1") == [TokenType.ADD, TokenType.INTEIRO]

def test_lexer_delimitadores_colados():
    assert _tipos("{x}") == [TokenType.LBRACE, TokenType.NOME, TokenType.RBRACE]
    assert _tipos("((1))") == [
        TokenType.LPAREN, TokenType.LPAREN, TokenType.INTEIRO, TokenType.RPAREN, TokenType.RPAREN
    ]
    assert _tipos("f(1,2)") == [
        TokenType.NOME, TokenType.LPAREN, TokenType.INTEIRO, TokenType.COMMA,
        TokenType.INTEIRO, TokenType.RPAREN
    ]
    assert _tipos("x:=1;") == [
        TokenType.NOME, TokenType.ASSIGN, TokenType.INTEIRO, TokenType.SEMICOLON
    ]
    assert _tipos(";;") == [TokenType.SEMICOLON, TokenType.SEMICOLON]

def test_lexer_expressao_sem_espacos():
    assert _tipos("var x:=2**3+4*5/6-7;") == [
        TokenType.VAR, TokenType.NOME, TokenType.ASSIGN, TokenType.INTEIRO, TokenType.POW,
        TokenType.INTEIRO, TokenType.ADD, TokenType.INTEIRO, TokenType.MULT, TokenType.INTEIRO,
        TokenType.DIV, TokenType.INTEIRO, TokenType.SUB, TokenType.INTEIRO, TokenType.SEMICOLON
    ]

def test_lexer_espacos_variados():
    esperado = [TokenType.VAR, TokenType.NOME, TokenType.ASSIGN, TokenType.INTEIRO, TokenType.SEMICOLON]
    assert _tipos("var x := 1;") == esperado
    assert _tipos("var\tx\t:=\t1\t;") == esperado
    assert _tipos("var\nx\n:=\n1\n;") == esperado
    assert _tipos("  var   x   :=   1   ;  ") == esperado
    assert _tipos("\n\n  var x := 1;\n\n") == esperado
    assert _tipos("var\r\nx :=\r\n1;") == esperado

def test_lexer_entrada_vazia_ou_so_espacos():
    for code in ["", " ", "   \n\t  \n"]:
        tokens = tokenizador(code)
        assert not isinstance(tokens, Erro), repr(code)
        assert len(tokens) == 0, repr(code)
