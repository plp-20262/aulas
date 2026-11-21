from algora import executar_programa
from tipos import Erro

# Testes de avaliação (semântica operacional) de records, campos e `this`
# (versão v3 de Algora).
#
# Fundamento: README.md §3.1 (Domínios Semânticos), §3.3 (FieldWrite,
# FieldWriteNaoLoc, FieldWriteNaoRec), §3.4 (RecordLit, NewRecord, FieldRead,
# FieldReadNaoLoc, FieldReadNaoRec, FieldReadAusente) e §3.5 (propagação
# monádica de erros).
#
# Regras-chave da semântica v3:
# - Records são localizações no store (`Loc`): `var q := p` copia a localização
#   (aliasing automático).
# - Campos de um literal `{ k1: e1, ..., kn: en }` são avaliados da esquerda
#   para a direita.
# - `e.n := e_rhs` avalia `e` antes de `e_rhs`; se `e` não for localização de
#   record, `e_rhs` NÃO é avaliada; atualiza o mapa relido após `e_rhs` e
#   insere o campo caso não exista (adição dinâmica).
# - `e.n` lê o campo `n` do record na localização denotada por `e`; ler campo
#   inexistente ou de não-record é erro.
# - `this` é variável comum (sem binding implícito), capturada lexicalmente
#   pelas closures.
# - Chamada de método `obj.m(args)` equivale a `(obj.m)(args)` (FieldRead + App).


# ---------------- Literais, leitura e escrita básica ----------------


def test_eval_record_literal_e_leitura_de_campos():
    prog = """
    var p := { x: 3, y: 4 };
    p.x + p.y
    """
    assert executar_programa(prog, {}, {}) == 7


def test_eval_record_vazio_e_adicao_dinamica_de_campo():
    # Regra (NewRecord) + (FieldWrite) com inserção de campo inexistente
    prog = """
    var p := {};
    p.z := 42;
    p.z
    """
    assert executar_programa(prog, {}, {}) == 42


def test_eval_atribuicao_atualiza_campo_existente_e_adiciona_novo():
    prog = """
    var p := { x: 1 };
    p.x := 10;
    p.y := 20;
    p.x + p.y
    """
    assert executar_programa(prog, {}, {}) == 30


def test_eval_campos_duplicados_ultimo_vence():
    # README §3.4: {k1 |-> v1, ...} com chaves repetidas: última associação vence,
    # mas todas as expressões são avaliadas da esquerda para a direita.
    prog = """
    var c := 0;
    var r := { x: { c := c + 1; 10 }, x: { c := c + 10; 20 } };
    r.x * 100 + c
    """
    assert executar_programa(prog, {}, {}) == 2011


def test_eval_records_aninhados_leitura_e_escrita():
    prog = """
    var a := { b: { c: 5 } };
    a.b.c := a.b.c + 10;
    a.b.c
    """
    assert executar_programa(prog, {}, {}) == 15


def test_eval_funcao_retornando_record():
    # README §2.1 / MANUAL §9.7: chaves duplas para retornar record de função
    prog = """
    def ponto(x, y) { { x: x, y: y } }
    var p := ponto(3, 4);
    p.x * 10 + p.y
    """
    assert executar_programa(prog, {}, {}) == 34


# ---------------- Aliasing e semântica de localizações ----------------


def test_eval_aliasing_atribuicao_de_variavel_copia_localizacao():
    # MANUAL §9.3: atribuir record a outra variável copia a localização, não o mapa
    prog = """
    var p := { x: 1 };
    var q := p;
    q.x := 99;
    p.x
    """
    assert executar_programa(prog, {}, {}) == 99


def test_eval_reatribuir_variavel_nao_altera_alias_antigo():
    prog = """
    var p := { x: 1 };
    var q := p;
    q := { x: 2 };
    p.x * 10 + q.x
    """
    assert executar_programa(prog, {}, {}) == 12


def test_eval_passagem_de_record_por_parametro_compartilha_localizacao():
    # Parâmetros são passados por valor, mas o valor de um record é sua localização (`Loc`)
    prog = """
    def zera(r) {
        r.x := 0;
        0
    }
    var p := { x: 55 };
    zera(p);
    p.x
    """
    assert executar_programa(prog, {}, {}) == 0


# ---------------- Ordem de avaliação e releitura do mapa ----------------


def test_eval_ordem_dos_campos_no_record_literal_esquerda_para_direita():
    prog = """
    var log := 0;
    def mark(d) { log := log * 10 + d; d }
    var r := { a: mark(1), b: mark(2), c: mark(3) };
    log
    """
    assert executar_programa(prog, {}, {}) == 123


def test_eval_field_write_avalia_base_antes_do_rhs():
    prog = """
    var log := 0;
    def mark(d) { log := log * 10 + d; d }
    var r := {};
    def get_r() { mark(1); r }
    get_r().x := mark(2);
    log * 10 + r.x
    """
    assert executar_programa(prog, {}, {}) == 122


def test_eval_field_write_nao_avalia_rhs_se_base_nao_for_record():
    # README §3.3: se `e` falhar (não for localização de record), `e_rhs` NÃO é avaliada
    prog = """
    var efeito := 0;
    var x := 5;
    x.n := { efeito := 1; 10 };
    efeito
    """
    res = executar_programa(prog, {}, {})
    assert isinstance(res, Erro)


def test_eval_field_write_rele_mapa_apos_efeito_do_rhs_por_aliasing():
    # README §3.3: o lado direito pode alterar o mesmo record por aliasing;
    # a atualização usa σ₂(ℓ), preservando alterações feitas durante `e_rhs`.
    prog = """
    var r := { a: 1 };
    def muta() {
        r.b := 20;
        10
    }
    r.a := muta();
    r.a + r.b
    """
    assert executar_programa(prog, {}, {}) == 30


# ---------------- Objetos, métodos, closures e `this` ----------------


def test_eval_metodo_como_campo_com_closure():
    # MANUAL §9.4 e §9.6: `obj.inc()` equivale a `(obj.inc)()`
    prog = """
    var obj := {};
    obj.n := 0;
    obj.inc := fn () { obj.n := obj.n + 1; obj.n };
    obj.inc();
    (obj.inc)();
    obj.n
    """
    assert executar_programa(prog, {}, {}) == 2


def test_eval_construtor_contador_com_this_instancias_independentes():
    # README §5 (Exemplo completo)
    prog = """
    def Contador() {
      var this := {};
      this.n := 0;
      this.inc := fn () { this.n := this.n + 1; this.n };
      this
    }

    var c1 := Contador();
    var c2 := Contador();
    c1.inc();
    c1.inc();
    c2.inc();
    c1.n + c2.n
    """
    assert executar_programa(prog, {}, {}) == 3


def test_eval_this_capturado_lexicalmente_sem_rebinding_implicito():
    # MANUAL §9.5: se um método é extraído para uma variável (`var f := c.inc`),
    # continua vendo o `this` de onde foi criado.
    prog = """
    def Contador() {
      var this := { n: 0 };
      this.inc := fn () { this.n := this.n + 1; this.n };
      this
    }
    var c := Contador();
    var f := c.inc;
    f();
    f();
    c.n
    """
    assert executar_programa(prog, {}, {}) == 2


def test_eval_this_como_parametro_de_funcao():
    # README §2 e §4: `this` pode ser parâmetro de `def` e de `fn`
    prog = """
    def soma_campo(this, d) {
        this.n := this.n + d;
        this.n
    }
    var obj := { n: 10 };
    soma_campo(obj, 5)
    """
    assert executar_programa(prog, {}, {}) == 15


# ---------------- Regras de erro e propagação ----------------


def test_eval_field_read_nao_loc_erro():
    # Regra (FieldReadNaoLoc): acessar campo de número ou closure é erro
    for prog in [
        "(5).n",
        "var x := 5; x.n",
        "var f := fn () { 1 }; f.n",
        "def g() { 1 } g.n",
    ]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog


def test_eval_field_read_ausente_erro():
    # Regra (FieldReadAusente): ler campo inexistente é erro
    for prog in [
        "var p := {}; p.x",
        "var p := { x: 1 }; p.y",
        "({ a: 10 }).b",
    ]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog


def test_eval_field_write_nao_loc_erro():
    # Regra (FieldWriteNaoLoc): atribuir campo em número ou closure é erro
    for prog in [
        "var x := 5; x.n := 1; x",
        "(5).n := 1; 0",
        "var f := fn () { 1 }; f.n := 1; 0",
        "def g() { 1 } g.n := 1; 0",
    ]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog


def test_eval_record_em_operadores_condicoes_e_chamada_eh_erro():
    # Um record (`Loc`) não é número nem closure: operadores, `if`, `while` e aplicação falham
    for prog in [
        "var r := {}; r + 1",
        "var r := {}; 1 + r",
        "var r := {}; -r",
        "var r := {}; +r",
        "var r := {}; r == r",
        "var r := {}; r < 1",
        "var r := {}; r()",
        "var r := {}; if r { 1 } else { 2 }",
        "var r := {}; while r { } 1",
    ]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog


def test_eval_propagacao_de_erros_em_records():
    # §3.5: erro dentro de literal de record, base ou RHS de campo propaga
    for prog in [
        "{ x: 1 / 0 }",
        "{ x: 1, y: nao_declarada }",
        "(1 / 0).x",
        "(1 / 0).x := 1; 0",
        "var r := {}; r.x := 1 / 0; 0",
    ]:
        res = executar_programa(prog, {}, {})
        assert isinstance(res, Erro), prog
