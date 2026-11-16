from algora import executar_programa
from tipos import Erro

def test_eval_divisao_por_zero_variantes():
    for prog in ["1 / 0", "0 / 0", "-1 / 0", "1 / (2 - 2)", "(1 + 2) / (3 - 3)",
                 "1 / (1 < 0)", "1 / 0 + 5", "5 + 1 / 0", "2 * (1 / 0)", "-(1 / 0)",
                 "(1 / 0) ** 2", "2 ** (1 / 0)", "1 / (0 * 5)", "1 / 0 / 1"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog
        assert "divisão por zero" in res.msg, prog

def test_eval_divisao_por_zero_com_variaveis_e_funcoes():
    res = executar_programa("var d := 0; 10 / d", {}, {})
    assert isinstance(res, Erro)
    assert "divisão por zero" in res.msg

    prog = """
    def div(a, b) { a / b }
    div(1, 0)
    """
    res = executar_programa(prog, {}, {})
    assert isinstance(res, Erro)
    assert "divisão por zero" in res.msg

    prog = """
    def div(a, b) { a / b }
    div(1, 2)
    """
    assert executar_programa(prog, {}, {}) == 0.5

def test_eval_divisao_por_zero_so_ocorre_se_a_expressao_for_avaliada():
    assert executar_programa("if 1 { 5 } else { 1 / 0 }", {}, {}) == 5
    assert executar_programa("if 0 { 1 / 0 } else { 5 }", {}, {}) == 5
    assert executar_programa("def f() { 1 / 0 } 5", {}, {}) == 5
    assert executar_programa("var f := fn () { 1 / 0 }; 5", {}, {}) == 5
    assert executar_programa("var x := 0; def g() { 1 / x } 7", {}, {}) == 7

def test_eval_erro_propaga_por_qualquer_contexto():
    for prog in ["var x := 1 / 0; 5",
                 "var x := 1; x := 1 / 0; 5",
                 "1 / 0; 5",
                 "{ 1 / 0 }",
                 "{ 1 / 0; 5 }",
                 "{ { { 1 / 0 } } }",
                 "if 1 / 0 { 1 } else { 2 }",
                 "if 1 { 1 / 0 } else { 2 }",
                 "(fn (x) { x })(1 / 0)",
                 "(fn () { 1 / 0 })()",
                 "def f(x) { x } f(1 / 0)",
                 "def f() { 1 / 0 } f() + 1",
                 "def f() { 1 / 0 } 1 + f()",
                 "def f() { 1 / 0 } def g() { f() } def h() { g() } h()",
                 "(1 / 0)(1)"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog

def test_eval_argumentos_sao_avaliados_mesmo_se_nao_usados():
    assert executar_programa("def k(a) { 1 } k(1)", {}, {}) == 1
    res = executar_programa("def k(a) { 1 } k(1 / 0)", {}, {})
    assert isinstance(res, Erro)
    assert "divisão por zero" in res.msg
    res = executar_programa("(fn (a, b) { a })(1, 1 / 0)", {}, {})
    assert isinstance(res, Erro)
    res = executar_programa("def k(a) { 1 } k(naoDeclarada)", {}, {})
    assert isinstance(res, Erro)

def test_eval_erro_em_comando_de_expressao_nao_e_engolido():
    assert executar_programa("var x := 1; x; 5", {}, {}) == 5
    for prog in ["x; 5", "1 / 0; 5", "f(); 5", "(fn () { y })(); 5", "1(2); 5",
                 "(fn (a) { a })(); 5", "{ z }; 5", "if w { 1 } else { 2 }; 5"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog

def test_eval_variavel_nao_ligada():
    assert executar_programa("var x := 0; x", {}, {}) == 0
    for prog in ["x", "x + 1", "1 + x", "-x", "x()", "f(1)", "(x)", "{ x }",
                 "if x { 1 } else { 2 }", "if 1 { x } else { 2 }",
                 "var y := x; y", "def f() { x } f()", "(fn () { x })()",
                 "def f(a) { b } f(1)", "def f(a) { a } f(b)"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog

def test_eval_nomes_sao_sensiveis_a_maiusculas():
    assert executar_programa("var x := 1; var X := 2; x * 10 + X", {}, {}) == 12
    for prog in ["var x := 1; X", "var Abc := 1; abc", "def Fat() { 1 } fat()"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog

def test_eval_atribuicao_a_variavel_nao_declarada():
    assert executar_programa("var y := 0; y := 1; y", {}, {}) == 1
    for prog in ["y := 1; 0", "x := x + 1; x", "{ y := 1; 0 }", "def f() { z := 1; 0 } f()",
                 "if 1 { y := 1; 0 } else { 0 }", "(fn () { y := 1; 0 })()"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog

def test_eval_atribuicao_fora_do_escopo_da_declaracao():
    for prog in ["{ var y := 1; y }; y := 2; y",
                 "def f() { var y := 1; y } f(); y := 2; 0",
                 "if 1 { var y := 1; y } else { 0 }; y := 2; 0"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog

def test_eval_chamada_de_nao_funcao():
    assert executar_programa("def f() { fn () { 1 } } f()()", {}, {}) == 1
    for prog in ["1(2)", "(1 + 2)(3)", "var x := 5; x()", "(1 < 2)(0)",
                 "def f() { 1 } f()()", "var n := 3; n(n)", "{ 7 }()", "-1(2)"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog

def test_eval_aridade_incorreta_mensagem():
    assert executar_programa("def f(a, b) { a + b } f(1, 2)", {}, {}) == 3
    for prog in ["(fn () { 1 })(1)",
                 "(fn (x) { x })()",
                 "(fn (x) { x })(1, 2)",
                 "def f(a, b) { a } f(1)",
                 "def f(a, b) { a } f(1, 2, 3)",
                 "def f() { 1 } f(0)",
                 "def f(a, b, c, d) { a } f(1, 2, 3)",
                 "def mk() { fn (a) { a } } mk()(1, 2)",
                 "def mk() { fn (a, b) { a } } mk()(1)",
                 "def add(a, b) { a + b } add(1)(2)"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog
        assert "aridade incorreta" in res.msg, prog

def test_eval_operadores_com_funcao_sao_erro():
    # os operadores são definidos apenas sobre ℝ (f_op lifted)
    for expr in ["f + 1", "1 + f", "f - 1", "f * 2", "f / 1", "f ** 2", "2 ** f",
                 "f + f", "-f", "+f", "f + g", "g * 2"]:
        prog = "var f := fn () { 1 }; def g() { 1 } " + expr
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), expr

def test_eval_if_condicao_funcao_mensagem():
    for prog in ["var f := fn () { 1 }; if f { 1 } else { 2 }",
                 "def g() { 1 } if g { 1 } else { 2 }",
                 "def g() { fn () { 1 } } if g() { 1 } else { 2 }",
                 "if { fn () { 1 } } { 1 } else { 2 }",
                 "if if 1 { fn () { 1 } } else { fn () { 2 } } { 1 } else { 2 }"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog
        assert "condição do 'if' é uma função" in res.msg, prog

def test_eval_erro_sintatico_vira_erro_de_execucao():
    for prog in ["var x := ;", "1 +", "if 1 { 2 }", "", "var x := 1;", "f(1,)", "1 < 2 < 3", "--1"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), repr(prog)

    res = executar_programa("var x := 1 x", {}, {})
    assert isinstance(res, Erro)
    assert "esperava ';'" in res.msg

    res = executar_programa("if 1 { 2 }", {}, {})
    assert isinstance(res, Erro)
    assert "esperava 'else'" in res.msg

    res = executar_programa("1 2", {}, {})
    assert isinstance(res, Erro)
    assert "tokens não consumidos" in res.msg

def test_eval_erro_lexico_vira_erro_de_execucao():
    for prog in ["1 @ 2", "var x := 1.5; x", "var ação := 1; ação", "x != 1", "@"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog
        assert "token desconhecido" in res.msg, prog
