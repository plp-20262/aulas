from algora import executar_programa
from tipos import Erro

def test_eval_if_qualquer_numero_diferente_de_zero_e_verdadeiro():
    assert executar_programa("if 5 { 1 } else { 2 }", {}, {}) == 1
    assert executar_programa("if -1 { 1 } else { 2 }", {}, {}) == 1
    assert executar_programa("if 100 { 1 } else { 2 }", {}, {}) == 1
    assert executar_programa("if 0 - 3 { 1 } else { 2 }", {}, {}) == 1

def test_eval_if_condicao_fracionaria_e_verdadeira():
    assert executar_programa("if 1 / 2 { 1 } else { 2 }", {}, {}) == 1
    assert executar_programa("if 1 / 4 { 1 } else { 2 }", {}, {}) == 1
    assert executar_programa("if 2 ** -3 { 1 } else { 2 }", {}, {}) == 1

def test_eval_if_condicao_zero_calculado_e_falsa():
    assert executar_programa("if 2 - 2 { 1 } else { 2 }", {}, {}) == 2
    assert executar_programa("if 0 * 5 { 1 } else { 2 }", {}, {}) == 2
    assert executar_programa("if 1 < 0 { 1 } else { 2 }", {}, {}) == 2
    assert executar_programa("if 0 / 5 { 1 } else { 2 }", {}, {}) == 2
    assert executar_programa("if -0 { 1 } else { 2 }", {}, {}) == 2

def test_eval_if_com_comparacoes():
    assert executar_programa("if 3 < 5 { 1 } else { 2 }", {}, {}) == 1
    assert executar_programa("if 5 < 3 { 1 } else { 2 }", {}, {}) == 2
    assert executar_programa("if 3 == 3 { 1 } else { 2 }", {}, {}) == 1
    assert executar_programa("if 3 == 4 { 1 } else { 2 }", {}, {}) == 2
    assert executar_programa("if (1 < 2) == (2 < 3) { 7 } else { 8 }", {}, {}) == 7

def test_eval_if_executa_apenas_o_ramo_escolhido():
    prog = """
    var x := 0;
    if 1 { x := x + 1; 0 } else { x := x + 100; 0 };
    x
    """
    assert executar_programa(prog, {}, {}) == 1
    prog = """
    var x := 0;
    if 0 { x := x + 1; 0 } else { x := x + 100; 0 };
    x
    """
    assert executar_programa(prog, {}, {}) == 100

def test_eval_if_valor_e_a_ultima_expressao_do_ramo():
    assert executar_programa("if 1 { 1; 2; 3 } else { 4 }", {}, {}) == 3
    assert executar_programa("if 0 { 4 } else { 1; 2; 3 }", {}, {}) == 3

def test_eval_if_declaracao_do_ramo_nao_vaza():
    res = executar_programa("if 1 { var y := 5; y } else { 0 }; y", {}, {})
    assert isinstance(res, Erro)
    assert executar_programa("var y := 1; if 1 { var y := 5; y } else { 0 }; y", {}, {}) == 1

def test_eval_if_atribuicao_no_ramo_persiste():
    assert executar_programa("var y := 1; if 1 { y := 5; 0 } else { 0 }; y", {}, {}) == 5

def test_eval_if_aninhado():
    assert executar_programa("if 1 { if 0 { 1 } else { 2 } } else { 3 }", {}, {}) == 2
    assert executar_programa("if 0 { 1 } else { if 0 { 2 } else { 3 } }", {}, {}) == 3
    assert executar_programa("if 1 { if 1 { if 1 { 4 } else { 5 } } else { 6 } } else { 7 }", {}, {}) == 4

def test_eval_else_if_simulado_com_bloco():
    prog = """
    def sinal(n) {
        if n < 0 { 0 - 1 } else { if n == 0 { 0 } else { 1 } }
    }
    sinal(-5) * 100 + sinal(0) * 10 + sinal(7)
    """
    assert executar_programa(prog, {}, {}) == -99

def test_eval_if_condicao_com_chamada_e_efeito():
    prog = """
    var n := 0;
    def tick() { n := n + 1; n }
    if tick() { n * 10 } else { 99 }
    """
    assert executar_programa(prog, {}, {}) == 10

def test_eval_if_condicao_bloco_if_e_parenteses():
    assert executar_programa("if { 0 } { 1 } else { 2 }", {}, {}) == 2
    assert executar_programa("if { var t := 5; t - 5 } { 1 } else { 2 }", {}, {}) == 2
    assert executar_programa("if if 1 { 0 } else { 1 } { 10 } else { 20 }", {}, {}) == 20
    assert executar_programa("if (1 < 2) { 1 } else { 2 }", {}, {}) == 1

def test_eval_if_como_argumento_e_valor():
    assert executar_programa("def f(x) { x * 2 } f(if 1 { 4 } else { 5 })", {}, {}) == 8
    assert executar_programa("var x := if 0 { 1 } else { 2 }; x", {}, {}) == 2
    assert executar_programa("1 + (if 1 { 2 } else { 3 })", {}, {}) == 3
    assert executar_programa("(if 1 { 2 } else { 3 }) * (if 0 { 4 } else { 5 })", {}, {}) == 10

def test_eval_if_pode_retornar_funcao():
    prog = """
    var f := if 1 { fn () { 1 } } else { fn () { 2 } };
    f()
    """
    assert executar_programa(prog, {}, {}) == 1

def test_eval_if_erro_na_condicao_propaga():
    for prog in ["if x { 1 } else { 2 }", "if 1 / 0 { 1 } else { 2 }", "if 1(2) { 1 } else { 2 }"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog

def test_eval_if_ramo_nao_escolhido_nao_e_avaliado():
    assert executar_programa("if 1 { 1 } else { x }", {}, {}) == 1
    assert executar_programa("if 0 { x } else { 2 }", {}, {}) == 2
    assert executar_programa("if 1 { 1 } else { 1(2) }", {}, {}) == 1
    assert executar_programa("if 1 { 1 } else { (fn () { 1 })(1) }", {}, {}) == 1
    assert executar_programa("var x := 0; if 1 { 1 } else { x := 1 / 0; 0 }; x", {}, {}) == 0

def test_eval_if_ramo_escolhido_com_erro_propaga():
    res = executar_programa("if 1 { x } else { 2 }", {}, {})
    assert isinstance(res, Erro)
    res = executar_programa("if 0 { 1 } else { 1 / 0 }", {}, {})
    assert isinstance(res, Erro)
