import pytest
from tipos import Erro
from tests.conftest import assert_error, assert_error_in_ast, token


class TestLetParserNormal:
    """Testes de parsing para let..in bem-formados."""

    # --- 1. LET BÁSICO ---
    @pytest.mark.parametrize("code,expected", [
        ("let x = 1 in x", ["let", "x", 1, "x"]),
        ("let x = 1 + 2 in x", ["let", "x", [token("+"), 1, 2], "x"]),
        ("let x = 1 in x + 2", ["let", "x", 1, [token("+"), "x", 2]]),
    ])
    def test_basic_let(self, parse, code, expected):
        assert parse(code) == expected

    # --- 2. LET ANINHADO ---
    @pytest.mark.parametrize("code,expected", [
        ("let x = 1 in let y = 2 in x + y",
         ["let", "x", 1, ["let", "y", 2, [token("+"), "x", "y"]]]),
        ("let x = 1 in let x = 2 in x",
         ["let", "x", 1, ["let", "x", 2, "x"]]),
    ])
    def test_nested_let(self, parse, code, expected):
        assert parse(code) == expected

    # --- 3. PRECEDÊNCIA ---
    @pytest.mark.parametrize("code,expected", [
        # let tem precedência mais baixa que operadores aditivos no corpo
        ("let x = 1 in x + 2", ["let", "x", 1, [token("+"), "x", 2]]),
        # let x = 1 + 2 in x  ==  let x = (1 + 2) in x
        ("let x = 1 + 2 in x", ["let", "x", [token("+"), 1, 2], "x"]),
        # let em expressão maior
        ("1 + let x = 2 in x * 3", [token("+"), 1, ["let", "x", 2, [token("*"), "x", 3]]]),
    ])
    def test_let_precedence(self, parse, code, expected):
        assert parse(code) == expected

    # --- 4. VARIÁVEIS ---
    @pytest.mark.parametrize("code,expected", [
        ("x", "x"),
        ("x + y", [token("+"), "x", "y"]),
        ("-x", [token("-"), "x"]),
        ("x ** 2", [token("**"), "x", 2]),
    ])
    def test_variables(self, parse, code, expected):
        assert parse(code) == expected

    # --- 5. EXPRESSÕES COMPLEXAS ---
    @pytest.mark.parametrize("code,expected", [
        ("let x = (1 + 2) in x", ["let", "x", [token("+"), 1, 2], "x"]),
        ("let x = -5 in x", ["let", "x", [token("-"), 5], "x"]),
    ])
    def test_complex_let(self, parse, code, expected):
        assert parse(code) == expected


class TestLetParserErrors:
    """Testes de parsing para erros em let..in."""

    # --- 1. PALAVRAS RESERVADAS COMO IDENTIFICADORES ---
    def test_let_as_var_name(self, parse):
        result = parse("let x = 1 in let")
        assert isinstance(result, Erro)
        assert "esperava nome após 'let'" in result.msg

    def test_in_as_var_name(self, parse):
        result = parse("let x = 1 in in")
        assert isinstance(result, Erro)
        assert "token inesperado 'in'" in result.msg

    # --- 2. LET MALFORMADO ---
    def test_missing_equal(self, parse):
        result = parse("let x 1 in x")
        assert isinstance(result, Erro)
        assert "esperava '=' após nome" in result.msg

    def test_missing_in(self, parse):
        result = parse("let x = 1 x")
        assert isinstance(result, Erro)
        assert "esperava 'in' após expressão de vinculação" in result.msg

    def test_missing_binding_expr(self, parse):
        result = parse("let x = in x")
        assert isinstance(result, Erro)
        assert "inesperado" in result.msg

    def test_missing_body(self, parse):
        result = parse("let x = 1 in")
        assert isinstance(result, Erro)
        assert "inesperado" in result.msg

    def test_missing_name_after_let(self, parse):
        result = parse("let = 1 in x")
        assert isinstance(result, Erro)
        assert "esperava nome após 'let'" in result.msg

    def test_let_empty(self, parse):
        result = parse("let")
        assert isinstance(result, Erro)

    # --- 3. ERROS DE VARIÁVEIS ---
    def test_var_starting_with_digit(self, parse):
        result = parse("1x")
        assert isinstance(result, Erro)
        assert "tokens depois da expressão" in result.msg

    def test_var_uppercase(self, parse):
        result = parse("X")
        assert isinstance(result, Erro)
        assert "token desconhecido 'X'" in result.msg

    # --- 4. ERROS DE EXPRESSÕES DENTRO DO LET ---
    def test_malformed_binding_expr(self, parse):
        result = parse("let x = 1 + in x")
        assert_error_in_ast(result)

    def test_malformed_body(self, parse):
        result = parse("let x = 1 in 1 +")
        assert_error_in_ast(result)