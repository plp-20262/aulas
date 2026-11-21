from algora import executar_programa
from tipos import Erro

# Testes de avaliação (semântica operacional) do comando `while`
# (versão v2 de Algora).
#
# Fundamento: README.md §3.3 (regras WhileFalso, WhileVerd, WhileCondFuncao e
# BlocoCmd) e §3.5 (convenção monádica de propagação de erros, agora estendida
# à relação Downarrow_s do corpo do laço).
#
# Regras-chave da semântica v2:
# - A condição é numérica: 0 é falso, qualquer outro real é verdadeiro.
# - Se falsa, o laço termina sem executar o corpo (WhileFalso).
# - Se verdadeira, o corpo é executado e o laço se repete a partir da memória
#   resultante (WhileVerd).
# - O corpo é um bloco de comandos sem expressão final; seu ambiente final é
#   descartado, mas a memória persiste entre iterações.
# - Um while_cmd não produz valor: não pode ser a última coisa do programa.
# - Condição que é função é erro (WhileCondFuncao).
# - Erros em qualquer premissa propagam para todo o laço.
#
# Nota: loop infinito (ex.: `while 1 { }`) é semântica parcial (não há
# derivação), portanto fica deliberadamente fora dos testes automáticos.


# ---------------- Avaliação válida ----------------


def test_eval_while_condicao_falsa_corpo_nao_executa():
    assert executar_programa("var i := 5; while i < 0 { } i", {}, {}) == 5


def test_eval_while_soma_0_ate_4():
    # Exemplo do README (§3.3): soma 0 + 1 + 2 + 3 + 4 = 10.
    prog = """
    var i := 0;
    var soma := 0;
    while i < 5 {
        soma := soma + i;
        i := i + 1;
    }
    soma
    """
    assert executar_programa(prog, {}, {}) == 10


def test_eval_while_contagem_regressiva():
    prog = """
    var n := 5;
    var r := 0;
    while 0 < n {
        r := r + n;
        n := n - 1;
    }
    r
    """
    assert executar_programa(prog, {}, {}) == 15


def test_eval_while_fatorial_de_7():
    prog = """
    def fatorial(n) {
        var fat := 1;
        while 0 < n {
            fat := fat * n;
            n := n - 1;
        }
        fat
    }
    fatorial(7)
    """
    assert executar_programa(prog, {}, {}) == 5040


def test_eval_while_fatorial_de_0_e_de_1():
    prog0 = """
    def fat(n) {
        var f := 1;
        while 0 < n {
            f := f * n;
            n := n - 1;
        }
        f
    }
    fat(0)
    """
    prog1 = """
    def fat(n) {
        var f := 1;
        while 0 < n {
            f := f * n;
            n := n - 1;
        }
        f
    }
    fat(1)
    """
    assert executar_programa(prog0, {}, {}) == 1
    assert executar_programa(prog1, {}, {}) == 1


def test_eval_while_corpo_nao_modifica_ambiente_apos_o_laco():
    # O ambiente do corpo é descartado: `x` declarado dentro não vaza.
    res = executar_programa("var i := 0; while i < 2 { var x := i; i := i + 1; } x", {}, {})
    assert isinstance(res, Erro)


def test_eval_while_cada_iteracao_aloca_novo_endereco_para_var_do_corpo():
    # Se `x` fosse compartilhado entre iterações, daria 3 (1 + 2); como cada
    # iteração aloca um endereço fresco, dá 2 (1 + 1).
    prog = """
    var i := 0;
    var r := 0;
    while i < 2 {
        var x := 0;
        x := x + 1;
        r := r + x;
        i := i + 1;
    }
    r
    """
    assert executar_programa(prog, {}, {}) == 2


def test_eval_while_memoria_persiste_entre_iteracoes():
    prog = """
    var i := 0;
    var s := 0;
    while i < 3 {
        s := s + 1;
        i := i + 1;
    }
    s
    """
    assert executar_programa(prog, {}, {}) == 3


def test_eval_while_expressao_final_apos_o_laco_é_o_resultado():
    assert executar_programa("var i := 0; while i < 2 { i := i + 1; } i * 10", {}, {}) == 20


def test_eval_while_multiplos_lacos_sequenciais_compartilham_memoria():
    prog = """
    var i := 0;
    while i < 2 { i := i + 1; }
    var j := 0;
    while j < i { j := j + 1; }
    j
    """
    assert executar_programa(prog, {}, {}) == 2


def test_eval_while_condicao_fracionaria_verdadeira():
    # Qualquer real != 0 é verdadeiro; 1/2 é verdadeiro.
    prog = """
    var i := 0;
    var x := 1 / 2;
    while x {
        i := 1;
        x := 0;
    }
    i
    """
    assert executar_programa(prog, {}, {}) == 1


# ---------------- Erros ----------------


def test_eval_while_erro_na_condicao_propaga():
    for prog in ["while x { } 1", "while 1 / 0 { } 1"]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog


def test_eval_while_erro_no_corpo_propaga():
    res = executar_programa("var i := 0; while i < 1 { 1 / 0; i := i + 1; } 1", {}, {})
    assert isinstance(res, Erro)


def test_eval_while_condicao_eh_funcao_mensagem():
    for prog in [
        "var f := fn () { 1 }; while f { } 1",
        "def g() { 1 } while g { } 1",
        "def g() { fn () { 1 } } while g() { } 1",
    ]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog


def test_eval_while_erro_antes_do_laco_propaga():
    res = executar_programa("1 / 0; while 0 { } 1", {}, {})
    assert isinstance(res, Erro)
