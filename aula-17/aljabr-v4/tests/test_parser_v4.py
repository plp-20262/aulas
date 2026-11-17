import pytest
from tipos import Erro
from tests.conftest import assert_error, parse_code


class TestParserV4:
    """Testes de aceitação do parser de `aljabr` v4.

    Estes testes codificam a EBNF de v4 (conforme README.md, seção 2). Devem
    falhar até que o parser seja atualizado (Fase 2).
    """

    # --- 1. DECLARAÇÕES DE TIPO (v4, §2) ---

    def test_type_decl_no_variants(self):
        """`type T = K` declara construtor sem componentes."""
        ast = parse_code("type T = K\n42")
        assert not isinstance(ast, Erro), f"Erro inesperado: {ast}"
        # 42 é a expressão final; a declaração de tipo deve ser consumida sem erro

    def test_type_decl_with_pipe(self):
        """`type T = A | B(x, y)` aceita múltiplas variantes separadas por |."""
        ast = parse_code("type T = A | B(x, y)\n42")
        assert not isinstance(ast, Erro), f"Erro inesperado: {ast}"

    def test_type_decl_zero_variants_is_error(self):
        """`type T =` sem variantes é erro de sintaxe."""
        ast = parse_code("type T =\n42")
        assert_error(ast)

    # --- 2. CONSTRUÇÃO DE VALORES ETIQUETADOS (atomo) ---

    def test_construir_valor_sem_componentes(self):
        """`Vazia` (sem parênteses) constrói valor etiquetado de aridade 0."""
        ast = parse_code("Vazia")
        assert not isinstance(ast, Erro), f"Erro inesperado: {ast}"

    def test_construir_valor_com_componentes(self):
        """`Cons(1, Vazia)` constrói valor etiquetado com componentes."""
        ast = parse_code("Cons(1, Vazia)")
        assert not isinstance(ast, Erro), f"Erro inesperado: {ast}"

    def test_construir_valor_aninhado(self):
        """`Cons(1, Cons(2, Vazia))` permite aninhamento."""
        ast = parse_code("Cons(1, Cons(2, Vazia))")
        assert not isinstance(ast, Erro), f"Erro inesperado: {ast}"

    def test_construir_valor_em_expressao_maior(self):
        """Valor etiquetado pode aparecer em expressões maiores."""
        ast = parse_code("Cons(1, Vazia) == Cons(1, Vazia)")
        assert not isinstance(ast, Erro), f"Erro inesperado: {ast}"

    # --- 3. EXPRESSÃO match ---

    def test_match_simples(self):
        """`match Vazia { Vazia => 0 }` é bem-formado."""
        ast = parse_code("match Vazia { Vazia => 0 }")
        assert not isinstance(ast, Erro), f"Erro inesperado: {ast}"

    def test_match_varios_ramos(self):
        """`match` aceita múltiplos ramos."""
        ast = parse_code("match x { Vazia => 0 Cons(_, r) => 1 }")
        assert not isinstance(ast, Erro), f"Erro inesperado: {ast}"

    def test_match_padrao_variavel(self):
        """Padrão variável (`NOME`) casa com qualquer valor."""
        ast = parse_code("match x { n => n }")
        assert not isinstance(ast, Erro), f"Erro inesperado: {ast}"

    def test_match_padrao_curinga(self):
        """Padrão curinga (`_`) casa com qualquer valor sem vincular."""
        ast = parse_code("match x { _ => 0 }")
        assert not isinstance(ast, Erro), f"Erro inesperado: {ast}"

    def test_match_padrao_inteiro(self):
        """Padrão literal inteiro casa com valores iguais."""
        ast = parse_code("match n { 0 => 1 _ => 2 }")
        assert not isinstance(ast, Erro), f"Erro inesperado: {ast}"

    def test_match_padrao_construtor_aninhado(self):
        """Padrão construtor com subpadrões aninhados."""
        ast = parse_code("match e { Add(Num(0), x) => x }")
        assert not isinstance(ast, Erro), f"Erro inesperado: {ast}"

    # --- 4. PROGRAMAS MAL-FORMADOS v4 (README.md, tabela) ---

    @pytest.mark.parametrize("code", [
        # construtor repetido na declaração de tipo
        "type T = A | A\n42",
        # nome de tipo minúsculo não é CONSTR
        "type T = vazia\n42",
        # `_` não pode ser vinculado em let
        "let _ = 1 in 2",
        # match sem ramos
        "match x { }",
        # variável repetida no padrão
        "match x { Add(a, a) => a }",
    ])
    def test_programas_mal_formados_sao_erro(self, code):
        ast = parse_code(code)
        assert isinstance(ast, Erro), f"Esperava Erro para {code!r}, obteve {ast!r}"
