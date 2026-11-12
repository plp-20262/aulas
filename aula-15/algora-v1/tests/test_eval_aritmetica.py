from algora import executar_programa
from tipos import Erro

def test_eval_precedencia_mult_sobre_soma():
    assert executar_programa("2 + 3 * 4", {}, {}) == 14
    assert executar_programa("2 * 3 + 4", {}, {}) == 10
    assert executar_programa("2 + 3 * 4 + 5", {}, {}) == 19
    assert executar_programa("10 - 2 * 3", {}, {}) == 4
    assert executar_programa("10 / 2 + 3", {}, {}) == 8
    assert executar_programa("3 + 10 / 2", {}, {}) == 8

def test_eval_associatividade_esquerda_subtracao():
    assert executar_programa("10 - 3 - 2", {}, {}) == 5
    assert executar_programa("10 - 3 - 2 - 1", {}, {}) == 4
    assert executar_programa("1 - 2 - 3", {}, {}) == -4
    assert executar_programa("10 - (3 - 2)", {}, {}) == 9

def test_eval_associatividade_esquerda_divisao():
    assert executar_programa("100 / 10 / 5", {}, {}) == 2
    assert executar_programa("8 / 4 / 2", {}, {}) == 1
    assert executar_programa("100 / (10 / 5)", {}, {}) == 50

def test_eval_associatividade_mista():
    assert executar_programa("10 - 2 + 3", {}, {}) == 11
    assert executar_programa("10 + 2 - 3", {}, {}) == 9
    assert executar_programa("10 / 4 * 2", {}, {}) == 5
    assert executar_programa("2 * 3 / 4", {}, {}) == 1.5
    assert executar_programa("12 / 3 * 2", {}, {}) == 8
    assert executar_programa("12 / (3 * 2)", {}, {}) == 2

def test_eval_divisao_e_real_e_nao_inteira():
    # o domínio de valores é ℝ: 7 / 2 não é 3
    assert executar_programa("7 / 2", {}, {}) == 3.5
    assert executar_programa("1 / 4", {}, {}) == 0.25
    assert executar_programa("-7 / 2", {}, {}) == -3.5
    assert executar_programa("3 / 2 == 1", {}, {}) == 0
    assert executar_programa("3 / 2 == 3 / 2", {}, {}) == 1
    assert executar_programa("1 / 2 + 1 / 2", {}, {}) == 1
    assert executar_programa("1 / 2 * 2", {}, {}) == 1

def test_eval_divisao_exata_e_com_zero_no_numerador():
    assert executar_programa("10 / 5", {}, {}) == 2
    assert executar_programa("0 / 5", {}, {}) == 0
    assert executar_programa("0 / -5", {}, {}) == 0

def test_eval_potencia_associatividade_direita():
    assert executar_programa("2 ** 3 ** 2", {}, {}) == 512
    assert executar_programa("2 ** 2 ** 3", {}, {}) == 256
    assert executar_programa("(2 ** 3) ** 2", {}, {}) == 64
    assert executar_programa("2 ** 2 ** 2 ** 2", {}, {}) == 65536

def test_eval_potencia_precede_multiplicacao_e_soma():
    assert executar_programa("2 * 3 ** 2", {}, {}) == 18
    assert executar_programa("3 ** 2 * 2", {}, {}) == 18
    assert executar_programa("2 ** 3 * 2", {}, {}) == 16
    assert executar_programa("2 + 3 ** 2", {}, {}) == 11
    assert executar_programa("10 - 2 ** 3", {}, {}) == 2
    assert executar_programa("16 / 2 ** 3", {}, {}) == 2
    assert executar_programa("2 ** 3 / 4", {}, {}) == 2

def test_eval_potencia_casos_basicos():
    assert executar_programa("5 ** 0", {}, {}) == 1
    assert executar_programa("5 ** 1", {}, {}) == 5
    assert executar_programa("0 ** 5", {}, {}) == 0
    assert executar_programa("1 ** 100", {}, {}) == 1
    assert executar_programa("2 ** 10", {}, {}) == 1024
    assert executar_programa("10 ** 3", {}, {}) == 1000
    assert executar_programa("2 ** 100", {}, {}) == 2 ** 100

def test_eval_potencia_com_expoente_negativo_ou_fracionario():
    assert executar_programa("2 ** -1", {}, {}) == 0.5
    assert executar_programa("2 ** -2", {}, {}) == 0.25
    assert executar_programa("4 ** (1 / 2)", {}, {}) == 2
    assert executar_programa("9 ** (1 / 2)", {}, {}) == 3

def test_eval_potencia_fora_de_r_nao_produz_valor_nao_real():
    # 0 elevado a expoente negativo é indefinido: deve ser Erro (e não uma exceção do host)
    res = executar_programa("0 ** -1", {}, {})
    assert isinstance(res, Erro)
    # raiz de negativo não está em ℝ: o resultado nunca pode ser um número complexo
    res = executar_programa("(-8) ** (1 / 3)", {}, {})
    assert not isinstance(res, complex)

def test_eval_unario_menos_e_mais():
    assert executar_programa("-5", {}, {}) == -5
    assert executar_programa("+5", {}, {}) == 5
    assert executar_programa("-(-5)", {}, {}) == 5
    assert executar_programa("- (2 + 3)", {}, {}) == -5
    assert executar_programa("-2 + 3", {}, {}) == 1
    assert executar_programa("-2 * 3", {}, {}) == -6
    assert executar_programa("-2 * -3", {}, {}) == 6
    assert executar_programa("-(-(-5))", {}, {}) == -5

def test_eval_sinal_unario_depois_de_operador_binario():
    assert executar_programa("2 - -3", {}, {}) == 5
    assert executar_programa("2 + -3", {}, {}) == -1
    assert executar_programa("2 * -3", {}, {}) == -6
    assert executar_programa("2 - +3", {}, {}) == -1
    assert executar_programa("+2 + +3", {}, {}) == 5
    assert executar_programa("1--2", {}, {}) == 3
    assert executar_programa("1+-2", {}, {}) == -1
    assert executar_programa("5-3-1", {}, {}) == 1
    assert executar_programa("2**-1", {}, {}) == 0.5

def test_eval_unario_precede_potencia():
    # fator ::= unario [ ** fator ]  →  "-2 ** 2" é (-2) ** 2 = 4, e não -(2 ** 2)
    assert executar_programa("-2 ** 2", {}, {}) == 4
    assert executar_programa("-2 ** 3", {}, {}) == -8
    assert executar_programa("(-2) ** 2", {}, {}) == 4
    assert executar_programa("-(2 ** 2)", {}, {}) == -4
    assert executar_programa("-2 ** -2", {}, {}) == 0.25
    assert executar_programa("-3 ** 2 + 1", {}, {}) == 10

def test_eval_unario_com_variavel_e_chamada():
    assert executar_programa("var x := 3; -x", {}, {}) == -3
    assert executar_programa("var x := 3; -x ** 2", {}, {}) == 9
    assert executar_programa("var x := 3; 2 ** -x", {}, {}) == 0.125
    assert executar_programa("def f(a) { a + 1 } -f(2)", {}, {}) == -3
    assert executar_programa("def f(a) { a + 1 } 10 - f(2)", {}, {}) == 7

def test_eval_chamada_precede_operadores():
    prog = """
    def f(a) { a + 1 }
    f(1) + f(2) * f(3)
    """
    assert executar_programa(prog, {}, {}) == 14
    prog = """
    def f(a) { a + 1 }
    f(2) ** 2
    """
    assert executar_programa(prog, {}, {}) == 9
    prog = """
    def f(a) { a + 1 }
    2 ** f(1)
    """
    assert executar_programa(prog, {}, {}) == 4

def test_eval_parenteses_alteram_precedencia():
    assert executar_programa("(1 + 2) * 3", {}, {}) == 9
    assert executar_programa("2 * (3 + 4)", {}, {}) == 14
    assert executar_programa("((2 + 3)) * ((4))", {}, {}) == 20
    assert executar_programa("(10 - 2) - 3", {}, {}) == 5
    assert executar_programa("10 - (2 - 3)", {}, {}) == 11

def test_eval_zero_e_sinais():
    assert executar_programa("0 - 5", {}, {}) == -5
    assert executar_programa("-0", {}, {}) == 0
    assert executar_programa("0 * -1", {}, {}) == 0
    assert executar_programa("007 + 003", {}, {}) == 10

def test_eval_cadeias_longas():
    soma = " + ".join(["1"] * 100)
    assert executar_programa(soma, {}, {}) == 100
    sub = "100" + " - 1" * 50
    assert executar_programa(sub, {}, {}) == 50
    prod = " * ".join(["2"] * 20)
    assert executar_programa(prod, {}, {}) == 2 ** 20
