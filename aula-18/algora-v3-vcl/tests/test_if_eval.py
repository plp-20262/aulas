from algora import executar_programa
from tipos import Erro

def test_eval_if_verdadeiro():
    prog = "if 1 { 10 } else { 20 }"
    assert executar_programa(prog, {}, {}) == 10

def test_eval_if_falso():
    prog = "if 0 { 10 } else { 20 }"
    assert executar_programa(prog, {}, {}) == 20

def test_eval_if_com_efeito_colateral():
    prog = """
    var x := 0;
    if 1 < 2 {
        x := 100;
        x
    } else {
        x := 200;
        x
    }
    """
    assert executar_programa(prog, {}, {}) == 100

def test_eval_if_condicao_funcao_erro():
    prog = "if fn () { 1 } { 10 } else { 20 }"
    res = executar_programa(prog, {}, {})
    assert isinstance(res, Erro)
    assert "condição do 'if' é uma função" in res.msg
