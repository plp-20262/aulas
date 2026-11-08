import pytest
from tipos import Erro, Token, TokenType
from lexer import tokenizador


class TestLexer:
    """Testes do analisador léxico."""

    # --- 1. LITERAIS ---
    @pytest.mark.parametrize("code,expected_tokens", [
        ("42", [(TokenType.INTEIRO, "42")]),
        ("0", [(TokenType.INTEIRO, "0")]),
    ])
    def test_literals(self, code, expected_tokens):
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        assert len(result) == len(expected_tokens)
        for (tok, (exp_type, exp_lexema)) in zip(result, expected_tokens):
            assert tok.type == exp_type
            assert tok.lexema == exp_lexema

    # Floats são gerados durante avaliação (divisão), não no léxico
    # Ponto (.) não é token válido -> erro léxico
    def test_float_not_in_lexer(self):
        result = tokenizador("3.14")
        assert isinstance(result, Erro)
        assert "token desconhecido '.'" in result.msg

    # --- 2. OPERADORES ---
    @pytest.mark.parametrize("code,expected_types", [
        ("+", [TokenType.ADD]),
        ("-", [TokenType.SUB]),
        ("*", [TokenType.MULT]),
        ("/", [TokenType.DIV]),
        ("**", [TokenType.POW]),
        ("=", [TokenType.EQUAL]),
    ])
    def test_single_operators(self, code, expected_types):
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        assert [t.type for t in result] == expected_types

    # --- 3. PARENTESES ---
    @pytest.mark.parametrize("code,expected_types", [
        ("(", [TokenType.LPAREN]),
        (")", [TokenType.RPAREN]),
        ("(1)", [TokenType.LPAREN, TokenType.INTEIRO, TokenType.RPAREN]),
    ])
    def test_parentheses(self, code, expected_types):
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        assert [t.type for t in result] == expected_types

    # --- 4. PALAVRAS RESERVADAS ---
    @pytest.mark.parametrize("code,expected_type", [
        ("let", TokenType.LET),
        ("in", TokenType.IN),
    ])
    def test_reserved_words(self, code, expected_type):
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        assert len(result) == 1
        assert result[0].type == expected_type
        assert result[0].lexema == code

    # --- 5. VARIÁVEIS (NOME) ---
    @pytest.mark.parametrize("code", [
        "x",
        "x1",
        "x_1",
        "variavel_longa",
        "foo_bar_baz",
    ])
    def test_valid_variables(self, code):
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        assert len(result) == 1
        assert result[0].type == TokenType.NOME
        assert result[0].lexema == code

    # --- 6. ESPAÇOS E QUEBRAS DE LINHA ---
    @pytest.mark.parametrize("code", [
        "1 + 2",
        "  1  +  \t\n  2  ",
        "1\n+\n2",
    ])
    def test_whitespace_ignored(self, code):
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        # Deve produzir 3 tokens: 1, +, 2
        assert len(result) == 3
        assert result[0].type == TokenType.INTEIRO
        assert result[1].type == TokenType.ADD
        assert result[2].type == TokenType.INTEIRO

    # --- 7. ERROS LÉXICOS ---
    @pytest.mark.parametrize("code,expected_substring", [
        ("@", "token desconhecido '@'"),
        ("X", "token desconhecido 'X'"),  # maiúscula não suportada
        ("#", "token desconhecido '#'"),
        ("$", "token desconhecido '$'"),
    ])
    def test_lexical_errors(self, code, expected_substring):
        result = tokenizador(code)
        assert isinstance(result, Erro)
        assert expected_substring in result.msg

    # --- 8. INPUT OPERATOR ---
    def test_input_operator(self):
        result = tokenizador("?")
        assert not isinstance(result, Erro)
        assert len(result) == 1
        assert result[0].type == TokenType.INPUT
        assert result[0].lexema == "?"

    # --- 9. COMBINAÇÕES COMPLEXAS ---
    def test_complex_expression(self):
        code = "let x = 1 + 2 in x * 3"
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        types = [t.type for t in result]
        expected = [
            TokenType.LET, TokenType.NOME, TokenType.EQUAL,
            TokenType.INTEIRO, TokenType.ADD, TokenType.INTEIRO,
            TokenType.IN, TokenType.NOME, TokenType.MULT, TokenType.INTEIRO
        ]
        assert types == expected