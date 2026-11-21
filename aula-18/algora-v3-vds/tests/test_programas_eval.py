from algora import executar_programa
from tipos import Erro

def test_eval_numerais_de_church():
    prog = """
    var zero := fn (f) { fn (x) { x } };
    def succ(n) { fn (f) { fn (x) { f(n(f)(x)) } } }
    def add(a, b) { fn (f) { fn (x) { a(f)(b(f)(x)) } } }
    def mul(a, b) { fn (f) { a(b(f)) } }
    var one := succ(zero);
    var two := succ(one);
    var three := add(one, two);
    var inc := fn (k) { k + 1 };
    three(inc)(0) * 10 + mul(two, three)(inc)(0)
    """
    assert executar_programa(prog, {}, {}) == 36

def test_eval_combinador_z():
    prog = """
    var Z := fn (f) {
        (fn (x) { f(fn (v) { x(x)(v) }) })(fn (x) { f(fn (v) { x(x)(v) }) })
    };
    var fat := Z(fn (self) { fn (n) { if n == 0 { 1 } else { n * self(n - 1) } } });
    fat(5)
    """
    assert executar_programa(prog, {}, {}) == 120

def test_eval_contagem_de_primos():
    prog = """
    def mod(a, b) { if a < b { a } else { mod(a - b, b) } }
    def temDivisor(n, d) {
        if n < d * d { 0 } else {
            if mod(n, d) == 0 { 1 } else { temDivisor(n, d + 1) }
        }
    }
    def primo(n) { if n < 2 { 0 } else { if temDivisor(n, 2) { 0 } else { 1 } } }
    def contaPrimos(n) { if n < 2 { 0 } else { primo(n) + contaPrimos(n - 1) } }
    contaPrimos(20)
    """
    assert executar_programa(prog, {}, {}) == 8

def test_eval_collatz():
    prog = """
    def mod(a, b) { if a < b { a } else { mod(a - b, b) } }
    def collatz(n, passos) {
        if n == 1 { passos } else {
            if mod(n, 2) == 0 { collatz(n / 2, passos + 1) } else { collatz(3 * n + 1, passos + 1) }
        }
    }
    collatz(6, 0) * 10 + collatz(3, 0)
    """
    assert executar_programa(prog, {}, {}) == 87

def test_eval_celula_de_memoria_com_getter_e_setter():
    prog = """
    var cell := 0;
    def get() { cell }
    def set(v) { cell := v; v }
    set(5);
    set(get() * 2);
    get()
    """
    assert executar_programa(prog, {}, {}) == 10

def test_eval_conta_bancaria_com_closures():
    prog = """
    def conta(saldo) {
        fn (op, valor) {
            if op == 0 {
                saldo := saldo + valor;
                saldo
            } else {
                if valor < saldo + 1 { saldo := saldo - valor; saldo } else { 0 - 1 }
            }
        }
    }
    var a := conta(100);
    var b := conta(50);
    a(0, 50);
    b(1, 20);
    a(1, 500) * 1000 + a(1, 30) * 10 + b(0, 0)
    """
    # a: 100 -> 150; saque de 500 falha (-1); saque de 30 -> 120; b: 50 -> 30
    assert executar_programa(prog, {}, {}) == -1000 + 1200 + 30

def test_eval_newton_para_raiz_quadrada_usa_aritmetica_real():
    prog = """
    def newton(x, g, n) {
        if n == 0 { g } else { newton(x, (g + x / g) / 2, n - 1) }
    }
    newton(16, 8, 20)
    """
    res = executar_programa(prog, {}, {})
    assert not isinstance(res, Erro)
    assert abs(res - 4) < 1e-9
