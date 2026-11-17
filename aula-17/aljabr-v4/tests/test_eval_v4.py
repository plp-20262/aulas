import pytest
from tipos import Erro
from tests.conftest import assert_error, run


class TestEvalV4:
    """Testes de aceitação do avaliador de `aljabr` v4.

    Estes testes codificam a semântica de v4 (conforme README.md, seção 3):
    (Cons), (ConsInvalido), relação `casa`, (Match), (MatchNenhum) e o ajuste
    de (IfCond) para condições não numéricas. Devem falhar até que o avaliador
    seja atualizado (Fase 3).
    """

    # --- 1. CONSTRUÇÃO DE VALORES ETIQUETADOS (Cons) ---

    def test_construir_valor_sem_componentes(self):
        """`Vazia` (aridade 0) avalia para si mesmo."""
        # Como não há representação de valor etiquetado ainda, este teste
        # documenta o comportamento esperado após a Fase 3.
        resultado = run("type T = Vazia\nVazia")
        assert not isinstance(resultado, Erro), f"Erro inesperado: {resultado}"

    def test_construir_valor_com_componentes(self):
        """`Cons(1, Vazia)` constrói valor etiquetado."""
        resultado = run("type T = Cons(h, t)\nCons(1, Vazia)")
        assert not isinstance(resultado, Erro), f"Erro inesperado: {resultado}"

    # --- 2. CONSTRUTOR NÃO DECLARADO (ConsInvalido) ---

    def test_construtor_nao_declarado_erro(self):
        """`Foo(1)` com Foo não declarado resulta em erro."""
        resultado = run("Foo(1)")
        assert_error(resultado, "não declarado")

    def test_aridade_errada_erro(self):
        """`Num()` com Num/1 declarado resulta em erro de aridade."""
        resultado = run("type T = Num(n)\nNum()")
        assert_error(resultado, "aridade")

    # --- 3. MATCH: PRIMEIRO RAMO QUE CASA (Match) ---

    def test_match_primeiro_ramo_que_casa(self):
        """O primeiro ramo que casa vence; os demais não são avaliados."""
        resultado = run("match 1 { 0 => 10 _ => 20 }")
        assert not isinstance(resultado, Erro), f"Erro inesperado: {resultado}"
        assert resultado == 20, f"Esperava 20, obteve {resultado}"

    def test_match_curinga_casa_com_tudo(self):
        """O curinga `_` casa com qualquer valor."""
        resultado = run("match 42 { _ => 7 }")
        assert not isinstance(resultado, Erro), f"Erro inesperado: {resultado}"
        assert resultado == 7, f"Esperava 7, obteve {resultado}"

    def test_match_variavel_vincula_valor(self):
        """Padrão variável vincula o valor ao corpo do ramo."""
        resultado = run("match 5 { n => n + 1 }")
        assert not isinstance(resultado, Erro), f"Erro inesperado: {resultado}"
        assert resultado == 6, f"Esperava 6, obteve {resultado}"

    def test_match_inteiro_casa_valor_igual(self):
        """Padrão inteiro casa apenas com o valor igual."""
        assert run("match 0 { 0 => 1 _ => 2 }") == 1
        assert run("match 1 { 0 => 1 _ => 2 }") == 2

    # --- 4. MATCH: NENHUM RAMO CASA (MatchNenhum) ---

    def test_match_nenhum_ramo_casa_erro(self):
        """Se nenhum ramo casa, o resultado é erro."""
        resultado = run("match Vazia { Cons(h, t) => 0 }")
        assert_error(resultado)

    def test_match_funcao_sem_ramo_correspondente(self):
        """`match` sobre função com ramos só de construtor resulta em erro."""
        resultado = run("match (fn (x) => x) { Num(n) => n }")
        assert_error(resultado)

    # --- 5. IFCOND AJUSTADO: CONDIÇÃO NÃO NUMÉRICA ---

    def test_if_condicao_nao_numerica_erro(self):
        """`if` com condição que não é número resulta em erro (v4, §3)."""
        # Condição é uma função (closure) -> erro
        resultado = run("if (fn (x) => x) then 1 else 2")
        assert_error(resultado)
        # Condição é um valor etiquetado -> erro (ajuste v4)
        resultado = run("type T = Num(n)\nif Num(1) then 1 else 2")
        assert_error(resultado)

    # --- 6. ERROS DE TEMPO DE EXECUÇÃO v4 ---

    def test_numero_mais_etiquetado_erro(self):
        """Operação aritmética sobre valor etiquetado resulta em erro."""
        resultado = run("type T = Num(n)\nNum(1) + 1")
        assert_error(resultado)

    def test_etiquetado_igual_etiquetado_erro(self):
        """Não há igualdade estrutural entre valores etiquetados."""
        resultado = run("type T = Num(n)\nNum(1) == Num(1)")
        assert_error(resultado)
