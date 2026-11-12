from algora import executar_programa
from tipos import Erro

def test_eval_closure_captura_variavel_por_referencia():
    assert executar_programa("var x := 1; var f := fn () { x }; x := 5; f()", {}, {}) == 5

def test_eval_closures_compartilham_a_mesma_variavel():
    prog = """
    var n := 0;
    var inc := fn () { n := n + 1; n };
    var get := fn () { n };
    inc();
    inc();
    get()
    """
    assert executar_programa(prog, {}, {}) == 2

    prog = """
    var x := 0;
    var a := fn () { x := x + 1; x };
    var b := fn () { x := x * 10; x };
    a(); b(); a();
    b()
    """
    assert executar_programa(prog, {}, {}) == 110

def test_eval_closure_escapa_de_bloco_com_estado_privado():
    prog = """
    var f := { var secret := 42; fn () { secret } };
    f()
    """
    assert executar_programa(prog, {}, {}) == 42

    prog = """
    var f := { var secret := 42; fn () { secret } };
    secret
    """
    res = executar_programa(prog, {}, {})
    assert isinstance(res, Erro)

    prog = """
    var counter := { var n := 0; fn () { n := n + 1; n } };
    counter();
    counter()
    """
    assert executar_programa(prog, {}, {}) == 2

def test_eval_closure_captura_parametro_distinto_por_chamada():
    prog = """
    def mk(a) { fn (b) { a + b } }
    var add2 := mk(2);
    var add10 := mk(10);
    add2(1) * 100 + add10(1)
    """
    assert executar_programa(prog, {}, {}) == 311

def test_eval_closure_ve_parametro_mutado_depois_da_criacao():
    prog = """
    def mk(a) {
        var g := fn () { a };
        a := a + 1;
        g
    }
    mk(1)()
    """
    assert executar_programa(prog, {}, {}) == 2

def test_eval_acumuladores_independentes():
    prog = """
    def makeAcc(start) {
        var total := start;
        fn (d) { total := total + d; total }
    }
    var a := makeAcc(100);
    var b := makeAcc(0);
    a(10);
    b(5);
    a(1) * 1000 + b(1)
    """
    assert executar_programa(prog, {}, {}) == 111006

def test_eval_objeto_com_metodos_via_if():
    prog = """
    def mk() {
        var n := 0;
        fn (op) {
            if op == 0 { n := n + 1; n } else { n }
        }
    }
    var c := mk();
    c(0);
    c(0);
    c(0);
    c(1)
    """
    assert executar_programa(prog, {}, {}) == 3

def test_eval_escopo_lexico_e_nao_dinamico():
    prog = """
    var x := 1;
    def f() { x }
    def g() { var x := 2; f() }
    g()
    """
    assert executar_programa(prog, {}, {}) == 1

    prog = """
    def f() { x }
    def g() { var x := 2; f() }
    g()
    """
    res = executar_programa(prog, {}, {})
    assert isinstance(res, Erro)

def test_eval_parametro_sombreia_variavel_externa():
    prog = """
    var x := 10;
    def f(x) { x + 1 }
    f(1) * 100 + x
    """
    assert executar_programa(prog, {}, {}) == 210

def test_eval_var_local_sombreia_parametro():
    assert executar_programa("def f(x) { var x := x + 1; x } f(1)", {}, {}) == 2
    assert executar_programa("def f(x) { var y := x; var x := 100; y } f(1)", {}, {}) == 1

def test_eval_funcao_de_ordem_superior():
    assert executar_programa("def apply(f, x) { f(x) } apply(fn (n) { n * n }, 7)", {}, {}) == 49

def test_eval_funcao_retorna_funcao_encadeada():
    assert executar_programa("def a() { fn () { fn () { 7 } } } a()()()", {}, {}) == 7

def test_eval_currying():
    prog = """
    def add(a) { fn (b) { fn (c) { a + b + c } } }
    add(1)(2)(3)
    """
    assert executar_programa(prog, {}, {}) == 6
    assert executar_programa("(fn (a) { fn (b) { a - b } })(10)(3)", {}, {}) == 7

def test_eval_composicao_de_funcoes():
    prog = """
    def compose(f, g) { fn (x) { f(g(x)) } }
    def inc(x) { x + 1 }
    def dbl(x) { x * 2 }
    compose(inc, dbl)(5) * 100 + compose(dbl, inc)(5)
    """
    assert executar_programa(prog, {}, {}) == 1112

def test_eval_aplicar_duas_vezes():
    prog = """
    def twice(f) { fn (x) { f(f(x)) } }
    twice(fn (x) { x * 2 })(3) * 100 + twice(twice(fn (x) { x + 1 }))(0)
    """
    assert executar_programa(prog, {}, {}) == 1204

def test_eval_funcao_escolhida_por_if_ou_bloco():
    assert executar_programa("(if 1 { fn (x) { x + 1 } } else { fn (x) { x - 1 } })(10)", {}, {}) == 11
    assert executar_programa("(if 0 { fn (x) { x + 1 } } else { fn (x) { x - 1 } })(10)", {}, {}) == 9
    assert executar_programa("{ fn () { 5 } }()", {}, {}) == 5
    assert executar_programa("{ var k := 3; fn (x) { x * k } }(4)", {}, {}) == 12

def test_eval_funcao_anonima_imediata():
    assert executar_programa("(fn (x) { x * x })(5)", {}, {}) == 25
    assert executar_programa("(fn () { 42 })()", {}, {}) == 42
    assert executar_programa("(fn (a, b, c) { a * 100 + b * 10 + c })(1, 2, 3)", {}, {}) == 123

def test_eval_funcao_com_varios_parametros_e_sem_parametros():
    prog = """
    def f(a, b, c, d, e) { a + b * 2 + c * 3 + d * 4 + e * 5 }
    f(1, 1, 1, 1, 1)
    """
    assert executar_programa(prog, {}, {}) == 15
    assert executar_programa("def z() { 42 } z() + z()", {}, {}) == 84

def test_eval_argumentos_complexos():
    prog = """
    def f(a, b) { a - b }
    f(1 + 2 * 3, f(10, 4))
    """
    assert executar_programa(prog, {}, {}) == 1

    prog = """
    def f(a, b, c) { a + b + c(1) }
    f(if 1 { 10 } else { 20 }, { 5 }, fn (x) { x * 100 })
    """
    assert executar_programa(prog, {}, {}) == 115

def test_eval_reatribuir_variavel_com_funcao():
    assert executar_programa("var f := fn (x) { x + 1 }; f := fn (x) { x + 2 }; f(0)", {}, {}) == 2

def test_eval_chamada_so_pelo_efeito_colateral():
    prog = """
    var x := 0;
    def inc() { x := x + 1; 0 }
    inc(); inc(); inc();
    x
    """
    assert executar_programa(prog, {}, {}) == 3
