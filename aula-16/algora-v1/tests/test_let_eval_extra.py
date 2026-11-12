from algora import executar_programa
from tipos import Erro

def test_eval_var_redeclaracao_no_mesmo_escopo():
    assert executar_programa("var x := 1; var x := 2; x", {}, {}) == 2
    assert executar_programa("var x := 1; var x := 2; var x := 3; x", {}, {}) == 3

def test_eval_var_redeclaracao_nao_altera_closure_anterior():
    # "var x" de novo aloca um NOVO endereço: a closure continua apontando para o antigo
    prog = """
    var x := 1;
    var f := fn () { x };
    var x := 2;
    f()
    """
    assert executar_programa(prog, {}, {}) == 1

    prog = """
    var x := 1;
    def f() { x }
    var x := 2;
    f() * 10 + x
    """
    assert executar_programa(prog, {}, {}) == 12

def test_eval_atribuicao_altera_closure_anterior():
    # já ":=" escreve no MESMO endereço, que a closure compartilha
    prog = """
    var x := 1;
    var f := fn () { x };
    x := 2;
    f()
    """
    assert executar_programa(prog, {}, {}) == 2

    prog = """
    var x := 1;
    def f() { x }
    x := 2;
    f() * 10 + x
    """
    assert executar_programa(prog, {}, {}) == 22

def test_eval_var_nao_enxerga_a_si_mesma_na_inicializacao():
    for prog in ["var x := x; x", "var y := y + 1; y", "var f := f(); 0"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog
    assert executar_programa("var x := 3; var x := x; x", {}, {}) == 3

def test_eval_var_com_fn_nao_permite_recursao_direta():
    # diferente de def, "var f := fn ..." não inclui f na closure
    prog = """
    var f := fn (n) { if n == 0 { 0 } else { f(n - 1) } };
    f(3)
    """
    res = executar_programa(prog, {}, {})
    assert isinstance(res, Erro)

def test_eval_recursao_via_declaracao_e_atribuicao():
    prog = """
    var f := 0;
    f := fn (n) { if n == 0 { 0 } else { n + f(n - 1) } };
    f(4)
    """
    assert executar_programa(prog, {}, {}) == 10

def test_eval_atribuicao_copia_valor_sem_aliasing():
    assert executar_programa("var a := 1; var b := a; b := 2; a", {}, {}) == 1
    assert executar_programa("var a := 1; var b := a; a := 5; b", {}, {}) == 1
    assert executar_programa("var a := 1; var b := a; a := 5; a + b", {}, {}) == 6

def test_eval_atribuicao_de_closure_compartilha_estado_interno():
    prog = """
    def mk() { var n := 0; fn () { n := n + 1; n } }
    var f := mk();
    var g := f;
    f();
    g();
    f()
    """
    assert executar_programa(prog, {}, {}) == 3

def test_eval_atribuicao_com_valor_de_if_bloco_e_fn():
    assert executar_programa("var x := 0; x := if 1 { 10 } else { 20 }; x", {}, {}) == 10
    assert executar_programa("var x := 0; x := { var t := 4; t * t }; x", {}, {}) == 16
    assert executar_programa("var x := 0; x := fn () { 7 }; x()", {}, {}) == 7

def test_eval_atribuicoes_com_dependencias_e_troca():
    assert executar_programa("var a := 1; var b := 2; a := b; b := a + 10; a * 100 + b", {}, {}) == 212
    prog = """
    var a := 1;
    var b := 2;
    var t := a;
    a := b;
    b := t;
    a * 10 + b
    """
    assert executar_programa(prog, {}, {}) == 21
    assert executar_programa("var x := 1; x := x + x * 2; x", {}, {}) == 3

def test_eval_atribuicao_a_variavel_externa_persiste_apos_bloco_e_funcao():
    assert executar_programa("var x := 1; { x := 2; 0 }; x", {}, {}) == 2
    assert executar_programa("var x := 0; def set(v) { x := v; v } set(9); x", {}, {}) == 9
    assert executar_programa("var x := 0; (fn () { x := 4; 0 })(); x", {}, {}) == 4

def test_eval_atribuicao_em_variavel_sombreada_nao_afeta_a_externa():
    prog = """
    var x := 1;
    { var x := 2; x := 3; x } * 10 + x
    """
    assert executar_programa(prog, {}, {}) == 31

def test_eval_atribuicao_a_nome_declarado_com_def():
    assert executar_programa("def f() { 1 } f := 5; f", {}, {}) == 5
    assert executar_programa("def f() { 1 } f := fn () { 2 }; f()", {}, {}) == 2
    res = executar_programa("def f() { 1 } f := 5; f()", {}, {})
    assert isinstance(res, Erro)

def test_eval_var_sombreia_def_e_def_sombreia_var():
    assert executar_programa("def f() { 7 } var f := 5; f", {}, {}) == 5
    assert executar_programa("var f := 5; def f() { 7 } f()", {}, {}) == 7

def test_eval_parametro_e_copia_do_argumento():
    prog = """
    var x := 1;
    def inc(a) { a := a + 1; a }
    inc(x) * 10 + x
    """
    assert executar_programa(prog, {}, {}) == 21

    prog = """
    def f(a) { a := a * 2; a }
    f(21)
    """
    assert executar_programa(prog, {}, {}) == 42

def test_eval_parametros_distintos_nao_fazem_alias():
    prog = """
    def f(a, b) { a := 10; b }
    var x := 1;
    f(x, x)
    """
    assert executar_programa(prog, {}, {}) == 1

    prog = """
    def f(a, b) { a := 10; a + b }
    var x := 1;
    f(x, x)
    """
    assert executar_programa(prog, {}, {}) == 11

def test_eval_var_local_de_funcao_e_nova_a_cada_chamada():
    prog = """
    def f(n) {
        var local := n;
        if n == 0 { 0 } else { f(n - 1); local }
    }
    f(3)
    """
    assert executar_programa(prog, {}, {}) == 3

def test_eval_declaracao_recebe_valor_de_comparacao():
    assert executar_programa("var t := 1 < 2; var f := 2 < 1; t * 10 + f", {}, {}) == 10
