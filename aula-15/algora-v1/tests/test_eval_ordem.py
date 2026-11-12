from algora import executar_programa

# "mark(d)" registra a ordem de avaliação: log := log * 10 + d
PRELUDIO = """
var log := 0;
def mark(d) {
    log := log * 10 + d;
    d
}
"""

def test_eval_ordem_dos_operandos_binarios_esquerda_para_direita():
    assert executar_programa(PRELUDIO + "mark(1) + mark(2); log", {}, {}) == 12
    assert executar_programa(PRELUDIO + "mark(1) - mark(2); log", {}, {}) == 12
    assert executar_programa(PRELUDIO + "mark(1) * mark(2); log", {}, {}) == 12
    assert executar_programa(PRELUDIO + "mark(1) / mark(2); log", {}, {}) == 12
    assert executar_programa(PRELUDIO + "mark(1) < mark(2); log", {}, {}) == 12
    assert executar_programa(PRELUDIO + "mark(1) == mark(2); log", {}, {}) == 12
    assert executar_programa(PRELUDIO + "mark(2) ** mark(3); log", {}, {}) == 23

def test_eval_ordem_de_operandos_encadeados():
    assert executar_programa(PRELUDIO + "mark(1) + mark(2) * mark(3); log", {}, {}) == 123
    assert executar_programa(PRELUDIO + "(mark(1) + mark(2)) * mark(3) - mark(4); log", {}, {}) == 1234

def test_eval_ordem_dos_argumentos_esquerda_para_direita():
    prog = PRELUDIO + """
    def f(a, b, c) { 0 }
    f(mark(1), mark(2), mark(3));
    log
    """
    assert executar_programa(prog, {}, {}) == 123

def test_eval_ordem_funcao_e_avaliada_antes_dos_argumentos():
    prog = PRELUDIO + """
    def g() {
        log := log * 10 + 9;
        fn (x) { x }
    }
    g()(mark(1));
    log
    """
    assert executar_programa(prog, {}, {}) == 91

def test_eval_ordem_condicao_antes_do_ramo():
    assert executar_programa(PRELUDIO + "if mark(1) { mark(2) } else { mark(3) }; log", {}, {}) == 12
    assert executar_programa(PRELUDIO + "if mark(1) - 1 { mark(2) } else { mark(3) }; log", {}, {}) == 13

def test_eval_efeito_do_operando_esquerdo_e_visivel_ao_direito():
    prog = """
    var x := 1;
    def bump() { x := x + 10; x }
    x + bump()
    """
    assert executar_programa(prog, {}, {}) == 12

    prog = """
    var x := 1;
    def bump() { x := x + 10; x }
    bump() + x
    """
    assert executar_programa(prog, {}, {}) == 22

    prog = """
    var x := 1;
    def bump() { x := x + 10; x }
    x - bump()
    """
    assert executar_programa(prog, {}, {}) == -10

def test_eval_efeito_em_blocos_como_operandos():
    prog = """
    var x := 1;
    { x := x + 1; x } - { x := x + 1; x }
    """
    assert executar_programa(prog, {}, {}) == -1

def test_eval_atribuicao_avalia_rhs_e_depois_grava():
    prog = """
    var x := 1;
    def bump() { x := x + 10; 0 }
    x := bump() + 5;
    x
    """
    assert executar_programa(prog, {}, {}) == 5

    prog = """
    var x := 1;
    def bump() { x := x + 10; x }
    x := x + bump();
    x
    """
    assert executar_programa(prog, {}, {}) == 12

def test_eval_var_avalia_rhs_no_ambiente_anterior_a_declaracao():
    assert executar_programa("var x := 1; var x := x + 1; x", {}, {}) == 2
    assert executar_programa("var x := 5; var x := x * x; var x := x + 1; x", {}, {}) == 26
    assert executar_programa("var x := 1; { var x := x + 10; x }", {}, {}) == 11
    assert executar_programa("var x := 1; var y := { var x := x + 1; x * 10 }; y + x", {}, {}) == 21

def test_eval_comandos_sao_executados_em_sequencia():
    prog = """
    var a := 1;
    a := a * 2;
    a := a + 3;
    a := a * 5;
    a
    """
    assert executar_programa(prog, {}, {}) == 25
