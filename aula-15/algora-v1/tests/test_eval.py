from algora import executar_programa
from tipos import Erro

def test_eval_aritimética_basica():
    assert executar_programa("1 + 2 * 3") == 7
    assert executar_programa("(1 + 2) * 3") == 9
    assert executar_programa("2 ** 3") == 8
    assert executar_programa("-10 + 5") == -5

def test_eval_comparacao():
    assert executar_programa("10 == 10") == 1
    assert executar_programa("10 == 5") == 0
    assert executar_programa("5 < 10") == 1
    assert executar_programa("10 < 5") == 0

def test_eval_divisao_por_zero():
    res = executar_programa("10 / 0")
    assert isinstance(res, Erro)
    assert "divisão por zero" in res.msg
