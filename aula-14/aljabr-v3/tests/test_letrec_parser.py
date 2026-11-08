import pytest
from tipos import Erro
from tests.conftest import token


class TestLetrecParserNormal:
    """Testes de parsing para letrec bem-formado (aljabr v3, §2)."""

    @pytest.mark.parametrize("code,expected", [
        ("letrec f = fn (x) => x in f",
         ["letrec", "f", ["fn", ["x"], "x"], "f"]),
        ("letrec f = fn (x, y) => x + y in f",
         ["letrec", "f", ["fn", ["x", "y"], [token("+"), "x", "y"]], "f"]),
        ("letrec f = fn () => 42 in f()",
         ["letrec", "f", ["fn", [], 42], ["app", "f", []]]),
    ])
    def test_letrec_well_formed(self, parse, code, expected):
        assert parse(code) == expected


class TestLetrecParserErrors:
    """Testes de parsing para erros em letrec (aljabr v3, §2)."""

    @pytest.mark.parametrize("code,msg_substring", [
        ("letrec x = 5 in x", "esperava 'fn' após '=' em 'letrec'"),
        ("letrec f = fn (x) => x in", "token inesperado"),
        ("letrec = fn (x) => x in x", "esperava nome após 'letrec'"),
    ])
    def test_malformed_letrec(self, parse, code, msg_substring):
        result = parse(code)
        assert isinstance(result, Erro)
        assert msg_substring in result.msg
