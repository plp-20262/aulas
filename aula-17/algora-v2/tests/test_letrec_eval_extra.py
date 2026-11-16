from algora import executar_programa
from tipos import Erro

def test_eval_def_nao_enxerga_declaracoes_posteriores():
    # a closure captura o ambiente do momento da declaração (sem "hoisting")
    for prog in ["def f() { g() } def g() { 1 } f()",
                 "def f() { y } var y := 1; f()",
                 "var f := fn () { y }; var y := 1; f()",
                 "var r := f(); def f() { 1 } r"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog
    assert executar_programa("def g() { 1 } def f() { g() } f()", {}, {}) == 1

def test_eval_recursao_mutua_via_atribuicao():
    prog = """
    var g := 0;
    def f() { g() }
    g := fn () { 1 };
    f()
    """
    assert executar_programa(prog, {}, {}) == 1

    prog = """
    var isOdd := 0;
    def isEven(n) { if n == 0 { 1 } else { isOdd(n - 1) } }
    isOdd := fn (n) { if n == 0 { 0 } else { isEven(n - 1) } };
    isEven(10) * 10 + isOdd(7)
    """
    assert executar_programa(prog, {}, {}) == 11

def test_eval_def_redefinicao_usa_a_ultima():
    assert executar_programa("def f() { 1 } def f() { 2 } f()", {}, {}) == 2

def test_eval_def_redefinicao_nao_altera_closure_anterior():
    prog = """
    def f() { 1 }
    def g() { f() }
    def f() { 2 }
    g() * 10 + f()
    """
    assert executar_programa(prog, {}, {}) == 12

def test_eval_parametro_com_mesmo_nome_da_funcao():
    assert executar_programa("def f(f) { f + 1 } f(5)", {}, {}) == 6
    assert executar_programa("def f(f) { f } f(7)", {}, {}) == 7
    assert executar_programa("def f(f) { f } f(7); f(8)", {}, {}) == 8

def test_eval_reatribuir_nome_da_def_afeta_chamadas_recursivas():
    # a recursão passa pelo endereço de f, que a atribuição sobrescreve
    prog = """
    def f(n) { if n == 0 { 0 } else { f(n - 1) } }
    var g := f;
    f := fn (n) { 100 };
    g(1)
    """
    assert executar_programa(prog, {}, {}) == 100

    prog = """
    def f(n) { if n == 0 { 0 } else { f(n - 1) } }
    var g := f;
    g(1)
    """
    assert executar_programa(prog, {}, {}) == 0

def test_eval_def_aninhado():
    prog = """
    def outer(n) {
        def inner(m) { m * 2 }
        inner(n) + 1
    }
    outer(5)
    """
    assert executar_programa(prog, {}, {}) == 11

def test_eval_def_aninhado_nao_vaza():
    prog = """
    def outer() { def inner() { 1 } inner() }
    outer()
    """
    assert executar_programa(prog, {}, {}) == 1
    prog = """
    def outer() { def inner() { 1 } inner() }
    outer();
    inner()
    """
    res = executar_programa(prog, {}, {})
    assert isinstance(res, Erro)

def test_eval_def_aninhado_captura_parametro_externo():
    assert executar_programa("def mk(a) { def add(b) { a + b } add } mk(10)(5)", {}, {}) == 15

def test_eval_def_aninhado_recursivo():
    prog = """
    def outer(n) {
        def loop(i, acc) {
            if i == 0 { acc } else { loop(i - 1, acc + i) }
        }
        loop(n, 0)
    }
    outer(10)
    """
    assert executar_programa(prog, {}, {}) == 55

def test_eval_def_dentro_de_bloco_e_if_nao_vaza():
    assert executar_programa("{ def f() { 5 } f() }", {}, {}) == 5
    assert executar_programa("if 1 { def f() { 5 } f() } else { 0 }", {}, {}) == 5
    res = executar_programa("{ def f() { 5 } f() }; f()", {}, {})
    assert isinstance(res, Erro)

def test_eval_def_como_valor():
    assert executar_programa("def f() { 3 } var g := f; g()", {}, {}) == 3
    prog = """
    def f(x) { x }
    def apply(h, v) { h(v) }
    apply(f, 9)
    """
    assert executar_programa(prog, {}, {}) == 9

def test_eval_recursao_fatorial_dez():
    prog = """
    def fat(n) { if n == 0 { 1 } else { n * fat(n - 1) } }
    fat(10)
    """
    assert executar_programa(prog, {}, {}) == 3628800

def test_eval_recursao_soma_ate_n():
    prog = """
    def soma(n) { if n == 0 { 0 } else { n + soma(n - 1) } }
    soma(40)
    """
    assert executar_programa(prog, {}, {}) == 820

def test_eval_recursao_fibonacci_dez():
    prog = """
    def fib(n) { if n < 2 { n } else { fib(n - 1) + fib(n - 2) } }
    fib(10)
    """
    assert executar_programa(prog, {}, {}) == 55

def test_eval_recursao_gcd_por_subtracao():
    prog = """
    def gcd(a, b) {
        if a == b { a } else {
            if a < b { gcd(a, b - a) } else { gcd(a - b, b) }
        }
    }
    gcd(48, 18) * 100 + gcd(17, 5) * 10 + gcd(7, 7)
    """
    assert executar_programa(prog, {}, {}) == 617

def test_eval_recursao_ackermann():
    prog = """
    def ack(m, n) {
        if m == 0 { n + 1 } else {
            if n == 0 { ack(m - 1, 1) } else { ack(m - 1, ack(m, n - 1)) }
        }
    }
    ack(0, 0) * 1000 + ack(1, 2) * 100 + ack(2, 2) * 10 + ack(2, 3)
    """
    assert executar_programa(prog, {}, {}) == 1000 + 400 + 70 + 9

def test_eval_recursao_potencia():
    prog = """
    def pw(b, e) { if e == 0 { 1 } else { b * pw(b, e - 1) } }
    pw(2, 10)
    """
    assert executar_programa(prog, {}, {}) == 1024

def test_eval_recursao_sem_def_passando_a_si_mesma():
    prog = """
    var f := fn (self, n) { if n == 0 { 1 } else { n * self(self, n - 1) } };
    f(f, 5)
    """
    assert executar_programa(prog, {}, {}) == 120
