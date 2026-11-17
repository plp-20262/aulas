import pytest
from tipos import Erro
from aljabr import Closure
from tests.conftest import assert_error, run, token


class TestLetRecEval:
    """Regras (LetRec) do avaliador (aljabr v3, §2).

    A primeira premissa de letrec é uma EQUAÇÃO: o nome fica auto-vinculado
    ao próprio closure antes de o corpo avaliar.
    """

    # --- 1. CASOS FELIZES ---
    @pytest.mark.parametrize("ast,expected", [
        # letrec f = fn (x) => x in f  — f aplicado, retorna o parâmetro
        (["letrec", "f", ["fn", ["x"], "x"], ["app", "f", [1]]], 1),
        # letrec f = fn () => 42 in f  — zero parâmetros
        (["letrec", "f", ["fn", [], 42], ["app", "f", []]], 42),
    ])
    def test_letrec_basic(self, eval_ast, env, ast, expected):
        assert eval_ast(ast, env) == expected

    # --- 2. AUTO-REFERÊNCIA: fatorial via if e comparação (ponta-a-ponta) ---
    def test_factorial_via_letrec(self):
        code = "letrec fat = fn (n) => if n == 0 then 1 else n * fat(n - 1) in fat(3)"
        assert run(code) == 6


class TestLetRecEvalErrors:
    """Erros envolvendo letrec."""

    def test_arity_error_in_letrec_body(self, eval_ast, env):
        ast = ["letrec", "f", ["fn", ["x", "y"], "x"], ["app", "f", [1]]]
        result = eval_ast(ast, env)
        assert isinstance(result, Erro)
        assert "aridade" in result.msg

    def test_letrec_error_in_body_propagates(self, eval_ast, env):
        """Erro no corpo do fn auto-vinculado se propaga (corpo é avaliado)."""
        ast = ["letrec", "f", ["fn", ["x"], [token("/"), "x", 0]], ["app", "f", [1]]]
        result = eval_ast(ast, env)
        assert isinstance(result, Erro)
        assert "divisão por zero" in result.msg

    def test_letrec_closure_is_value(self, eval_ast, env):
        """O vínculo ρ[f ↦ clo] é um Closure — valor de primeira classe."""
        result = eval_ast(["letrec", "f", ["fn", ["x"], "x"], "f"], env)
        assert isinstance(result, Closure)
        assert not isinstance(result, Erro)
