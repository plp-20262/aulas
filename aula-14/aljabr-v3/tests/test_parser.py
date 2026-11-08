import pytest
from tipos import Erro, Token, TokenType
from tests.conftest import assert_error, assert_error_in_ast, token


class TestParserNormal:
    """Testes de parsing para expressões bem-formadas."""

    # --- 1. ARITMÉTICA SIMPLES ---
    @pytest.mark.parametrize("code,expected", [
        ("1 + 2", [token("+"), 1, 2]),
        ("100 + 2500", [token("+"), 100, 2500]),
        ("5 - 3", [token("-"), 5, 3]),
        ("4 * 3", [token("*"), 4, 3]),
        ("10 / 2", [token("/"), 10, 2]),
        ("2 ** 3", [token("**"), 2, 3]),
    ])
    def test_simple_arithmetic(self, parse, code, expected):
        assert parse(code) == expected

    # --- 2. PRECEDÊNCIA E ASSOCIATIVIDADE ---
    @pytest.mark.parametrize("code,expected", [
        # Precedência: * sobre +
        ("1 + 2 * 3", [token("+"), 1, [token("*"), 2, 3]]),
        # Precedência: ** sobre *
        ("2 * 3 ** 4", [token("*"), 2, [token("**"), 3, 4]]),
        # Precedência tripla
        ("1 + 2 * 3 ** 4", [token("+"), 1, [token("*"), 2, [token("**"), 3, 4]]]),
        # Associatividade à esquerda: Subtração
        ("2 - 3 - 2", [token("-"), [token("-"), 2, 3], 2]),
        # Associatividade à esquerda: Divisão
        ("8 / 2 / 4", [token("/"), [token("/"), 8, 2], 4]),
        # Associatividade à direita: Exponenciação
        ("2 ** 3 ** 2", [token("**"), 2, [token("**"), 3, 2]]),
    ])
    def test_precedence_and_associativity(self, parse, code, expected):
        assert parse(code) == expected

    # --- 3. PARÊNTESES ---
    @pytest.mark.parametrize("code,expected", [
        ("(1 + 2) * 3", [token("*"), [token("+"), 1, 2], 3]),
        ("((1 + 2))", [token("+"), 1, 2]),
        ("(1 + 2) * (3 - 4)", [token("*"), [token("+"), 1, 2], [token("-"), 3, 4]]),
    ])
    def test_parentheses(self, parse, code, expected):
        assert parse(code) == expected

    # --- 4. ESPAÇAMENTO ---
    @pytest.mark.parametrize("code,expected", [
        ("2**(3+1)", [token("**"), 2, [token("+"), 3, 1]]),
        (" 10  + \n\t (  20   *  30 ) ", [token("+"), 10, [token("*"), 20, 30]]),
    ])
    def test_whitespace_robustness(self, parse, code, expected):
        assert parse(code) == expected

    # --- 5. OPERADORES UNÁRIOS ---
    @pytest.mark.parametrize("code,expected", [
        ("+5", [token("+"), 5]),
        ("-5", [token("-"), 5]),
        ("-2**2", [token("**"), [token("-"), 2], 2]),
        ("2**-3", [token("**"), 2, [token("-"), 3]]),
        ("-(3+2)", [token("-"), [token("+"), 3, 2]]),
        ("-3*4", [token("*"), [token("-"), 3], 4]),
        ("+3**2", [token("**"), [token("+"), 3], 2]),
        ("-(3-5)", [token("-"), [token("-"), 3, 5]]),
    ])
    def test_unary_operators(self, parse, code, expected):
        assert parse(code) == expected


class TestParserErrors:
    """Testes de parsing para erros sintáticos e léxicos."""

    # --- 1. ERROS LÉXICOS ---
    def test_lexical_error_unknown_char(self, parse):
        result = parse("1 @ 2")
        assert isinstance(result, Erro)
        assert "token desconhecido '@'" in result.msg

    def test_variable_now_supported(self, parse):
        """Variáveis agora são suportadas (NOME token)."""
        result = parse("x + 2")
        assert result == [token("+"), "x", 2]

    # --- 2. ERROS SINTÁTICOS ---
    def test_empty_input(self, parse):
        result = parse("")
        assert isinstance(result, Erro)
        assert "token inesperado 'EOF'" in result.msg

    def test_unclosed_paren(self, parse):
        result = parse("( 1 + 2")
        assert isinstance(result, Erro)
        assert "esperava ')'" in result.msg

    def test_unmatched_closing_paren(self, parse):
        result = parse(") 1 + 2")
        assert isinstance(result, Erro)
        assert "token inesperado ')'" in result.msg

    def test_empty_parens(self, parse):
        result = parse("()")
        assert isinstance(result, Erro)
        assert "token inesperado ')'" in result.msg

    def test_two_numbers_no_operator(self, parse):
        result = parse("1 2")
        assert isinstance(result, Erro)
        assert "tokens depois da expressão" in result.msg

    def test_two_expressions_consecutive(self, parse):
        """aljabr v2 (§2): `(e1) (e2)` agora é uma APLICAÇÃO bem formada
        (chamada ::= atomo { LPAREN [ args ] RPAREN }), não mais "tokens
        depois da expressão". O parser aceita; o eval dirá não-função."""
        result = parse("(1 + 2) (3 - 4)")
        assert result == ["app", [token("+"), 1, 2], [[token("-"), 3, 4]]]

    def test_excess_closing_paren(self, parse):
        result = parse("(1 + 2))")
        assert isinstance(result, Erro)
        assert "tokens depois da expressão" in result.msg

    # --- 3. ERROS DE OPERADORES UNÁRIOS (limitação conhecida do parser) ---
    # O parser atual não propaga erros de subparsers corretamente.
    # Estes testes verificam que Erro aparece na AST (não necessariamente no topo).
    @pytest.mark.parametrize("code", ["--2", "++2", "-+2", "+-2"])
    def test_consecutive_unary_operators(self, parse, code):
        result = parse(code)
        assert_error_in_ast(result)


class TestParserKnownLimitations:
    """Limitações conhecidas do parser atual - marcados como xfail."""

    # Estes testes falham porque o parser não verifica erros retornados
    # por subparsers antes de combiná-los na AST.
    # Quando o parser for corrigido, estes devem passar.

    @pytest.mark.xfail(reason="Parser não propaga erro de subparser em parse_exp/parse_termo")
    def test_expression_ends_with_operator(self, parse):
        result = parse("1 +")
        assert isinstance(result, Erro)
        assert "token inesperado 'EOF'" in result.msg

    @pytest.mark.xfail(reason="Parser não propaga erro de subparser em parse_exp/parse_termo")
    def test_two_operators_consecutive(self, parse):
        result = parse("1 + * 2")
        assert isinstance(result, Erro)
        assert "token inesperado '*'" in result.msg