import pytest
from tests.conftest import run


class TestErasure:
    """Apagamento de tipos (§4.4): `Bool` não existe na execução — os
    literais booleanos viram 1/0, e as comparações continuam devolvendo
    1/0. O helper `run` cobre lexer → parser → eval."""

    @pytest.mark.parametrize("code,expected", [
        ("verdadeiro", 1),
        ("falso", 0),
        ("let x = 5 in x < 10", 1),    # tipo Bool, valor (execução) 1
        ("let x = 10 in x < 10", 0),
        ("let x = 5 in x == 5", 1),
        ("let x = 5 in x == 6", 0),
        ("if verdadeiro then 7 else 8", 7),  # verdadeiro ⇒ 1 ⇒ ramo then
        ("if falso then 7 else 8", 8),       # falso ⇒ 0 ⇒ ramo else
        # booleans como argumentos também viram números na execução
        ("let f = fn (x: Num, y: Num) => x + y in f(verdadeiro, falso)", 1),
    ])
    def test_boolean_erasure(self, code, expected):
        assert run(code) == expected
