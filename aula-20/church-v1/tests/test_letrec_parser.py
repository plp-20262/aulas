import pytest
from tipos import Erro, TNum
from tests.conftest import token


class TestLetrecParserNormal:
    """Testes de parsing para letrec bem-formado (church v1, §4.2).

    O letrec agora tem tipo de retorno: a AST ganha um 5º elemento.
        letrec ::= letrec NOME = fn LPAREN [ params ] RPAREN : tipo => exp in exp
    """

    @pytest.mark.parametrize("code,expected", [
        ("letrec f = fn (x: Num) : Num => x in f",
         ["letrec", "f", ["fn", [("x", TNum())], "x"], TNum(), "f"]),
        ("letrec f = fn (x: Num, y: Num) : Num => x + y in f",
         ["letrec", "f", ["fn", [("x", TNum()), ("y", TNum())], [token("+"), "x", "y"]], TNum(), "f"]),
        ("letrec f = fn () : Num => 42 in f()",
         ["letrec", "f", ["fn", [], 42], TNum(), ["app", "f", []]]),
    ])
    def test_letrec_well_formed(self, parse, code, expected):
        assert parse(code) == expected


class TestLetrecParserErrors:
    """Testes de parsing para erros em letrec (church v1, §4.2)."""

    @pytest.mark.parametrize("code,msg_substring", [
        ("letrec x = 5 in x", "esperava 'fn' após '=' em 'letrec'"),
        ("letrec f = fn (x: Num) : Num => x in", "token inesperado"),
        ("letrec = fn (x: Num) : Num => x in x", "esperava nome após 'letrec'"),
        # church v1: o letrec exige o tipo de retorno (entre ')' e '=>')
        ("letrec f = fn (x: Num) => x in f", "esperava ':' (tipo de retorno)"),
    ])
    def test_malformed_letrec(self, parse, code, msg_substring):
        result = parse(code)
        assert isinstance(result, Erro)
        assert msg_substring in result.msg
