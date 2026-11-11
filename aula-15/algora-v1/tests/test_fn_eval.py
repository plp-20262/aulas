from algora import executar_programa
from tipos import Erro

def test_eval_funcao_anonima():
    prog = "(fn (x, y) { x + y })(3, 4)"
    assert executar_programa(prog) == 7

def test_eval_closure_estado_mutavel_camelcase():
    prog = """
    def criaContador() {
        var n := 0;
        fn () {
            n := n + 1;
            n
        }
    }

    var contador := criaContador();
    contador();
    contador();
    contador()
    """
    assert executar_programa(prog) == 3

def test_eval_closure_independente():
    prog = """
    def criaContador() {
        var n := 0;
        fn () {
            n := n + 1;
            n
        }
    }

    var c1 := criaContador();
    var c2 := criaContador();
    c1();
    c1();
    c2();
    c1() + c2()
    """
    assert executar_programa(prog) == 5

def test_eval_aridade_incorreta():
    prog = """
    var f := fn (x, y) { x + y };
    f(1)
    """
    res = executar_programa(prog)
    assert isinstance(res, Erro)
    assert "aridade incorreta" in res.msg
