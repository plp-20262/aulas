from algora import executar_programa
from tipos import Erro

def test_eval_execucoes_independentes_nao_compartilham_estado():
    prog = "var n := 0; def inc() { n := n + 1; n } inc(); inc(); inc()"
    assert executar_programa(prog, {}, {}) == 3
    assert executar_programa(prog, {}, {}) == 3
    assert executar_programa(prog, {}, {}) == 3

def test_eval_variavel_de_um_programa_nao_vaza_para_outro():
    assert executar_programa("var vazou := 1; vazou", {}, {}) == 1
    res = executar_programa("vazou", {}, {})
    assert isinstance(res, Erro)

    assert executar_programa("def vazou() { 1 } vazou()", {}, {}) == 1
    res = executar_programa("vazou()", {}, {})
    assert isinstance(res, Erro)

def test_eval_valor_final_pode_ser_funcao():
    for prog in ["fn (x) { x }", "def f() { 1 } f", "(fn () { fn () { 1 } })()",
                 "var f := fn () { 1 }; f"]:
        res = executar_programa(prog, {}, {})
        assert not isinstance(res, Erro), prog

def test_eval_valor_dos_comandos_anteriores_e_descartado():
    assert executar_programa("1; 2; 3", {}, {}) == 3
    assert executar_programa("var x := 5; x; x + 1", {}, {}) == 6
    assert executar_programa("{ 1; 2 }; 3", {}, {}) == 3
    assert executar_programa("fn () { 1 }; 4", {}, {}) == 4
    assert executar_programa("if 1 { 2 } else { 3 }; 4", {}, {}) == 4

def test_eval_espacamento_e_irrelevante():
    assert executar_programa("var x:=1;x+1", {}, {}) == 2
    assert executar_programa("var\tx\t:=\t10\t;\tx", {}, {}) == 10
    assert executar_programa("\n\n  var x := 1 ;\n\n x \n\n", {}, {}) == 1
    assert executar_programa("def f(a,b){a+b}f(1,2)", {}, {}) == 3
    assert executar_programa("if 1{2}else{3}", {}, {}) == 2
    assert executar_programa("(fn(x){x*2})(4)", {}, {}) == 8
    assert executar_programa("{1}+{2}", {}, {}) == 3

def test_eval_muitos_comandos_sequenciais():
    prog = "var x := 0;\n" + "x := x + 1;\n" * 200 + "x"
    assert executar_programa(prog, {}, {}) == 200

def test_eval_muitas_declaracoes_encadeadas():
    prog = "var v0 := 0;\n"
    for i in range(1, 101):
        prog += f"var v{i} := v{i - 1} + 1;\n"
    prog += "v100"
    assert executar_programa(prog, {}, {}) == 100

def test_eval_parenteses_e_blocos_aninhados():
    assert executar_programa("(" * 20 + "7" + ")" * 20, {}, {}) == 7
    assert executar_programa("{ " * 20 + "7" + " }" * 20, {}, {}) == 7
    assert executar_programa("({ (" * 8 + "7" + ") })" * 8, {}, {}) == 7

def test_eval_nomes_proximos_de_reservadas_funcionam_como_variaveis():
    prog = """
    var iffy := 1;
    var elsewhere := 2;
    var define := 3;
    var fnord := 4;
    var variable := 5;
    var IF := 6;
    var Else := 7;
    iffy + elsewhere + define + fnord + variable + IF + Else
    """
    assert executar_programa(prog, {}, {}) == 28

def test_eval_nomes_com_underscore():
    assert executar_programa("var _ := 1; var __x := 2; var x_1 := 3; _ + __x + x_1", {}, {}) == 6
