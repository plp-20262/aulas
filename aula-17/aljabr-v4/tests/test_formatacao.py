import pytest
from tipos import Erro
from aljabr import Tagged, Closure, formatar_valor


class TestFormatacao:
    """Testes de aceitação da formatação simplificada de valores (v4)."""

    # --- 1. VALORES ETIQUETADOS (Tagged) ---

    def test_tagged_vazio_sem_parenteses(self):
        """Tagged sem argumentos imprime apenas a tag, sem parênteses."""
        v = Tagged("VaziaLista", ())
        assert formatar_valor(v) == "VaziaLista"

    def test_tagged_com_um_argumento(self):
        v = Tagged("Num", (7,))
        assert formatar_valor(v) == "Num(7)"

    def test_tagged_com_varios_argumentos(self):
        v = Tagged("No", (2, Tagged("Vazia", ()), Tagged("Vazia", ())))
        assert formatar_valor(v) == "No(2, Vazia, Vazia)"

    def test_tagged_aninhado(self):
        v = Tagged("Cons", (1, Tagged("Cons", (2, Tagged("VaziaLista", ())))))
        assert formatar_valor(v) == "Cons(1, Cons(2, VaziaLista))"

    # --- 2. NÚMEROS ---

    def test_inteiro(self):
        assert formatar_valor(42) == "42"

    def test_float(self):
        assert formatar_valor(3.5) == "3.5"

    def test_zero(self):
        assert formatar_valor(0) == "0"

    # --- 3. ERROS ---

    def test_erro(self):
        v = Erro("divisão por zero")
        resultado = formatar_valor(v)
        assert "Erro" in resultado
        assert "divisão por zero" in resultado

    # --- 4. CLOSURES ---

    def test_fechamento(self):
        v = Closure(("x",), None, {})
        assert formatar_valor(v) == "<funcao>"
