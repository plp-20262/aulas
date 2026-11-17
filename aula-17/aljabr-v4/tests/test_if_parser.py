import pytest
from tipos import Erro
from tests.conftest import token


class TestIfParserNormal:
    """Testes de parsing para if..then..else bem-formado (aljabr v3, §2)."""

    @pytest.mark.parametrize("code,expected", [
        ("if 1 then 2 else 3", ["if", 1, 2, 3]),
        ("if x then 1 else 2", ["if", "x", 1, 2]),
        ("if 0 then 2 else 3", ["if", 0, 2, 3]),
        # condição é uma exp completa: comparações já caem no nível comp
        ("if 1 == 1 then 5 else 6", ["if", [token("=="), 1, 1], 5, 6]),
        # ramos são exp completo: o else aceita adição
        ("if 1 then 2 else 3 + 4", ["if", 1, 2, [token("+"), 3, 4]]),
        # let/fn são exp e podem aparecer nos ramos
        ("if 1 then let x = 2 in x else 3", ["if", 1, ["let", "x", 2, "x"], 3]),
        ("if 1 then 2 else fn (x) => x", ["if", 1, 2, ["fn", ["x"], "x"]]),
    ])
    def test_if_well_formed(self, parse, code, expected):
        assert parse(code) == expected


class TestIfParserErrors:
    """Testes de parsing para erros em if..then..else (aljabr v3, §2)."""

    @pytest.mark.parametrize("code", [
        "if x then 1",               # else obrigatório
        "if x then 2 else",         # corpo do else ausente
        "if x 2 else 3",            # then obrigatório
        "if",                        # expressão ausente
        "1 + if 1 then 2 else 3",  # if não é um átomo (sem parênteses não é exp)
        "let if = 1 in if",         # if é palavra reservada: não serve de NOME
    ])
    def test_malformed_if(self, parse, code):
        result = parse(code)
        assert isinstance(result, Erro)
