import pytest
from tipos import Erro
from tests.conftest import assert_error, token


class TestIfEval:
    """Regras (IfVerd)/(IfFalso)/(IfCond) do avaliador (aljabr v3, §2)."""

    # --- 1. CONDICÃO VERDADEIRAIRA (n ≠ 0) → ramo THEN ---
    @pytest.mark.parametrize("ast,expected", [
        (["if", 1, 2, 3], 2),
        (["if", -1, 10, 20], 10),  # n ≠ 0: sinal não importa
        (["if", 0, 10, 20], 20),   # n = 0 → IfFalso
    ])
    def test_if_verd(self, eval_ast, env, ast, expected):
        assert eval_ast(ast, env) == expected

    # --- 2. CONDICÃO FALSA (n = 0) → ramo ELSE ---
    @pytest.mark.parametrize("ast,expected", [
        (["if", 0, 2, 3], 3),
        (["if", 0, 10, 20], 20),
    ])
    def test_if_falso(self, eval_ast, env, ast, expected):
        assert eval_ast(ast, env) == expected

    # --- 3. CONDIÇÃO COMPARATIVA ---
    def test_if_with_comparison(self, eval_ast, env):
        ast = ["if", [token("=="), 1, 1], 5, 6]
        assert eval_ast(ast, env) == 5

    def test_if_with_comparison_false(self, eval_ast, env):
        ast = ["if", [token("<"), 5, 2], 5, 6]
        assert eval_ast(ast, env) == 6

    # --- 4. ERROS ---
    def test_if_condition_error_propagates(self, eval_ast, env):
        """⟨c,ρ⟩⇓erro ⇒ resultado erro (propagação monádica, §3)."""
        result = eval_ast(["if", [token("/"), 1, 0], 2, 3], env)
        assert_error(result, "divisão por zero")

    def test_if_unbound_var_in_condition(self, eval_ast, env):
        result = eval_ast(["if", "x", 2, 3], env)
        assert_error(result, "variável 'x' não vinculada")

    def test_if_condition_is_closure(self, eval_ast, env):
        """(IfCond): condição que avalia para closure ⇒ erro."""
        result = eval_ast(["if", ["fn", ["x"], "x"], 2, 3], env)
        assert isinstance(result, Erro)
        assert "condição de 'if'" in result.msg

    # --- 5. FALTA DE STRICTNESS: ramos não escolhidos não são avaliados ---
    def test_if_lazy_then_branch(self, eval_ast, env):
        """Se cond = 1, o else (com 1/0) nunca é avaliado."""
        assert eval_ast(["if", 1, 2, [token("/"), 1, 0]], env) == 2

    def test_if_lazy_else_branch(self, eval_ast, env):
        """Se cond = 0, o then (com 1/0) nunca é avaliado."""
        assert eval_ast(["if", 0, [token("/"), 1, 0], 3], env) == 3
