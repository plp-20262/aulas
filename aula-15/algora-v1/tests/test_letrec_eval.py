from algora import executar_programa

def test_eval_funcao_recursiva_fatorial():
    prog = """
    def fat(n) {
        if n == 0 {
            1
        } else {
            n * fat(n - 1)
        }
    }
    fat(5)
    """
    assert executar_programa(prog) == 120

def test_eval_funcao_recursiva_fibonacci():
    prog = """
    def fib(n) {
        if n < 2 {
            n
        } else {
            fib(n - 1) + fib(n - 2)
        }
    }
    fib(6)
    """
    assert executar_programa(prog) == 8
