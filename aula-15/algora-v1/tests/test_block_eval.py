from algora import executar_programa
from tipos import Erro

def test_eval_bloco_retorna_a_ultima_expressao():
    assert executar_programa("{ 1 }", {}, {}) == 1
    assert executar_programa("{ 1; 2; 3 }", {}, {}) == 3
    assert executar_programa("{ var x := 4; x * 2 }", {}, {}) == 8

def test_eval_bloco_como_operando():
    assert executar_programa("1 + { 2 }", {}, {}) == 3
    assert executar_programa("{ 1 } + { 2 }", {}, {}) == 3
    assert executar_programa("{ 2 } ** { 3 }", {}, {}) == 8
    assert executar_programa("-{ 3 }", {}, {}) == -3
    assert executar_programa("{ 10 } / { 4 }", {}, {}) == 2.5
    assert executar_programa("2 * { 3 } + { 4 } * 5", {}, {}) == 26

def test_eval_blocos_aninhados():
    assert executar_programa("{ { { 5 } } }", {}, {}) == 5
    assert executar_programa("{ var a := 1; { var b := 2; { var c := 3; a + b + c } } }", {}, {}) == 6

def test_eval_bloco_nao_vaza_declaracoes():
    res = executar_programa("{ var y := 1; y }; y", {}, {})
    assert isinstance(res, Erro)
    res = executar_programa("{ def f() { 1 } f() }; f()", {}, {})
    assert isinstance(res, Erro)
    res = executar_programa("{ { var z := 1; z }; z }", {}, {})
    assert isinstance(res, Erro)

def test_eval_bloco_sombreia_e_restaura():
    prog = """
    var x := 1;
    { var x := 2; { var x := 3; x } + x } * 10 + x
    """
    assert executar_programa(prog, {}, {}) == 51

def test_eval_bloco_atribuicao_em_varios_niveis_persiste():
    assert executar_programa("var x := 0; { { { x := 7; 0 }; 0 }; 0 }; x", {}, {}) == 7
    assert executar_programa("var x := 0; { x := 5; 0 }; { x := x * 2; 0 }; x", {}, {}) == 10

def test_eval_bloco_inicializador_ve_variavel_externa_de_mesmo_nome():
    assert executar_programa("var x := 1; var y := { var x := 10; x + 1 }; x * 100 + y", {}, {}) == 111

def test_eval_bloco_como_valor_de_funcao_e_argumento():
    assert executar_programa("var f := { fn (x) { x + 1 } }; f(1)", {}, {}) == 2
    assert executar_programa("def f(a, b) { a - b } f({ 10 }, { var t := 3; t })", {}, {}) == 7

def test_eval_bloco_com_def_local():
    assert executar_programa("{ def sq(n) { n * n } sq(5) + sq(2) }", {}, {}) == 29

def test_eval_bloco_chamado_enxerga_variaveis_externas():
    assert executar_programa("var x := 7; { fn () { x } }()", {}, {}) == 7
