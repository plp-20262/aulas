from algora import executar_programa
from tipos import Erro

def test_eval_comparacao_produz_numero_1_ou_0():
    assert executar_programa("(1 < 2) + (2 < 3)", {}, {}) == 2
    assert executar_programa("(1 == 1) * 10", {}, {}) == 10
    assert executar_programa("(1 < 2) + 1", {}, {}) == 2
    assert executar_programa("(2 < 1) + 1", {}, {}) == 1
    assert executar_programa("(1 == 1) == 1", {}, {}) == 1
    assert executar_programa("(1 < 2) == (2 < 3)", {}, {}) == 1
    assert executar_programa("(1 < 2) == (2 < 1)", {}, {}) == 0

def test_eval_menor_que_casos_de_borda():
    assert executar_programa("1 < 1", {}, {}) == 0
    assert executar_programa("0 < 1", {}, {}) == 1
    assert executar_programa("0 < 0", {}, {}) == 0
    assert executar_programa("-1 < 0", {}, {}) == 1
    assert executar_programa("-2 < -1", {}, {}) == 1
    assert executar_programa("-1 < -2", {}, {}) == 0
    assert executar_programa("1 / 2 < 1", {}, {}) == 1
    assert executar_programa("1 < 1 / 2", {}, {}) == 0

def test_eval_igualdade_casos_de_borda():
    assert executar_programa("0 == 0", {}, {}) == 1
    assert executar_programa("0 == -0", {}, {}) == 1
    assert executar_programa("-1 == -1", {}, {}) == 1
    assert executar_programa("1 == 2", {}, {}) == 0
    assert executar_programa("2 - 2 == 0", {}, {}) == 1
    assert executar_programa("1 / 2 == 1 / 2", {}, {}) == 1
    assert executar_programa("1 / 2 == 0", {}, {}) == 0
    assert executar_programa("2 ** 3 == 8", {}, {}) == 1

def test_eval_comparacao_tem_precedencia_menor_que_aritmetica():
    assert executar_programa("1 + 2 < 2 * 2", {}, {}) == 1
    assert executar_programa("5 - 3 < 3", {}, {}) == 1
    assert executar_programa("1 == 1 + 1", {}, {}) == 0
    assert executar_programa("2 * 3 == 6", {}, {}) == 1
    assert executar_programa("1 + 1 == 2", {}, {}) == 1
    assert executar_programa("2 ** 3 == 4 * 2", {}, {}) == 1
    assert executar_programa("10 - 5 < 2 * 2", {}, {}) == 0

def test_eval_comparacao_encadeada_so_com_parenteses():
    assert executar_programa("(1 < 2) < 3", {}, {}) == 1
    assert executar_programa("(2 < 1) < 1", {}, {}) == 1
    assert executar_programa("(1 == 1) == (2 == 2)", {}, {}) == 1
    assert executar_programa("1 < (2 < 3)", {}, {}) == 0

def test_eval_comparacao_encadeada_sem_parenteses_erro():
    for prog in ["1 < 2 < 3", "1 == 1 == 1", "1 < 2 == 1", "1 == 1 < 2"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog

def test_eval_comparacao_com_variaveis_e_chamadas():
    prog = """
    var a := 3;
    var b := 4;
    def dobro(n) { n * 2 }
    (a < b) * 100 + (dobro(a) == 6) * 10 + (dobro(b) < a)
    """
    assert executar_programa(prog, {}, {}) == 110

def test_eval_comparacao_com_blocos_e_if():
    assert executar_programa("{ 1 } < { 2 }", {}, {}) == 1
    assert executar_programa("{ 2 } == { 2 }", {}, {}) == 1
    assert executar_programa("(if 1 { 5 } else { 6 }) == 5", {}, {}) == 1

def test_eval_comparacao_com_funcao_erro():
    for prog in ["f == f", "f == 1", "1 == f", "f < 1", "1 < f", "f < f"]:
        res = executar_programa("var f := fn () { 1 }; " + prog, {}, {})
        assert isinstance(res, Erro), prog
