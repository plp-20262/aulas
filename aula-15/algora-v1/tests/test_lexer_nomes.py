from lexer import tokenizador
from tipos import TokenType, Erro

def test_lexer_nomes_com_underscore_e_digitos():
    for nome in ["_", "__", "_x", "x_", "x1", "x_1", "_1", "a1b2c3",
                 "snake_case", "camelCase", "ABC", "MixedCase_9"]:
        tokens = tokenizador(nome)
        assert not isinstance(tokens, Erro), nome
        assert len(tokens) == 1, nome
        assert tokens[0].type == TokenType.NOME, nome
        assert tokens[0].lexema == nome, nome

def test_lexer_reservadas_sao_sensiveis_a_maiusculas():
    # palavras reservadas são apenas as minúsculas; as demais são NOME
    for nome in ["VAR", "Var", "DEF", "Def", "FN", "Fn", "IF", "If", "ELSE", "Else"]:
        tokens = tokenizador(nome)
        assert not isinstance(tokens, Erro), nome
        assert len(tokens) == 1, nome
        assert tokens[0].type == TokenType.NOME, nome
        assert tokens[0].lexema == nome, nome

def test_lexer_prefixo_de_reservada_e_nome():
    for nome in ["variable", "variavel", "vars", "var1", "var_", "define", "default",
                 "fnord", "fn2", "iffy", "if1", "elsewhere", "else_", "elseif", "ifelse"]:
        tokens = tokenizador(nome)
        assert not isinstance(tokens, Erro), nome
        assert len(tokens) == 1, nome
        assert tokens[0].type == TokenType.NOME, nome
        assert tokens[0].lexema == nome, nome

def test_lexer_reservada_no_meio_ou_fim_de_nome():
    for nome in ["xvar", "my_if", "a_else", "undef", "myfn", "_def", "x_fn_y"]:
        tokens = tokenizador(nome)
        assert not isinstance(tokens, Erro), nome
        assert len(tokens) == 1, nome
        assert tokens[0].type == TokenType.NOME, nome

def test_lexer_lexema_das_reservadas():
    tokens = tokenizador("var def fn if else")
    assert not isinstance(tokens, Erro)
    assert [t.lexema for t in tokens] == ["var", "def", "fn", "if", "else"]

def test_lexer_reservadas_coladas_em_simbolos():
    tokens = tokenizador("if(x){y}else{z}")
    assert not isinstance(tokens, Erro)
    assert [t.type for t in tokens] == [
        TokenType.IF, TokenType.LPAREN, TokenType.NOME, TokenType.RPAREN,
        TokenType.LBRACE, TokenType.NOME, TokenType.RBRACE,
        TokenType.ELSE, TokenType.LBRACE, TokenType.NOME, TokenType.RBRACE
    ]

    tokens = tokenizador("fn(x){x}")
    assert not isinstance(tokens, Erro)
    assert [t.type for t in tokens] == [
        TokenType.FN, TokenType.LPAREN, TokenType.NOME, TokenType.RPAREN,
        TokenType.LBRACE, TokenType.NOME, TokenType.RBRACE
    ]

    tokens = tokenizador("def f(){1}")
    assert not isinstance(tokens, Erro)
    assert [t.type for t in tokens] == [
        TokenType.FUNCTION, TokenType.NOME, TokenType.LPAREN, TokenType.RPAREN,
        TokenType.LBRACE, TokenType.INTEIRO, TokenType.RBRACE
    ]

def test_lexer_inteiros_multi_digito():
    tokens = tokenizador("0 7 42 1000 9876543210")
    assert not isinstance(tokens, Erro)
    assert [t.type for t in tokens] == [TokenType.INTEIRO] * 5
    assert [int(t.lexema) for t in tokens] == [0, 7, 42, 1000, 9876543210]

def test_lexer_inteiro_com_zeros_a_esquerda():
    # INTEIRO ::= [0-9]+  (zeros à esquerda são permitidos)
    tokens = tokenizador("007 00 0123")
    assert not isinstance(tokens, Erro)
    assert [t.type for t in tokens] == [TokenType.INTEIRO] * 3
    assert [int(t.lexema) for t in tokens] == [7, 0, 123]

def test_lexer_inteiro_colado_em_nome():
    # a análise léxica é gulosa: "1x" são dois tokens (a rejeição é papel do parser)
    tokens = tokenizador("1x")
    assert not isinstance(tokens, Erro)
    assert [t.type for t in tokens] == [TokenType.INTEIRO, TokenType.NOME]

    tokens = tokenizador("12ab3")
    assert not isinstance(tokens, Erro)
    assert [t.type for t in tokens] == [TokenType.INTEIRO, TokenType.NOME]
    assert tokens[1].lexema == "ab3"

def test_lexer_inteiro_colado_em_reservada():
    tokens = tokenizador("1if")
    assert not isinstance(tokens, Erro)
    assert [t.type for t in tokens] == [TokenType.INTEIRO, TokenType.IF]
