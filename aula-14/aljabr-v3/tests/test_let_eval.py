import pytest
from tipos import Erro
from aljabr import Environment
from tests.conftest import assert_error, token


class TestLetEvalVariables:
    """Testes de lookup de variáveis no avaliador."""

    def test_existing_variable(self, eval_ast):
        assert eval_ast("x", {"x": 5}) == 5

    def test_float_variable(self, eval_ast):
        assert eval_ast("x", {"x": 3.14}) == 3.14

    def test_error_in_env_lifted(self, eval_ast):
        """Ambiente lifted: Erro no ambiente propaga."""
        assert eval_ast("x", {"x": Erro("RUNTIME: teste")}) == Erro("RUNTIME: teste")

    def test_unbound_variable(self, eval_ast):
        assert_error(eval_ast("x", {}), "variável 'x' não vinculada")
        assert_error(eval_ast("y", {"x": 1}), "variável 'y' não vinculada")


class TestLetEvalBasic:
    """Testes básicos de let..in no avaliador."""

    @pytest.mark.parametrize("ast,expected", [
        (["let", "x", 1, "x"], 1),
        (["let", "x", [token("+"), 1, 2], "x"], 3),
        (["let", "x", 1, [token("+"), "x", 2]], 3),
        (["let", "x", 2, [token("*"), "x", 3]], 6),
    ])
    def test_basic_let(self, eval_ast, env, ast, expected):
        assert eval_ast(ast, env) == expected


class TestLetEvalNested:
    """Testes de let aninhado e shadowing."""

    def test_nested_let(self, eval_ast, env):
        ast = ["let", "x", 1, ["let", "y", 2, [token("+"), "x", "y"]]]
        assert eval_ast(ast, env) == 3

    def test_shadowing(self, eval_ast, env):
        ast = ["let", "x", 1, ["let", "x", 2, "x"]]
        assert eval_ast(ast, env) == 2

    def test_outer_var_accessible(self, eval_ast, env):
        ast = ["let", "x", 1, ["let", "y", 2, [token("+"), "x", "y"]]]
        assert eval_ast(ast, env) == 3


class TestLetEvalOperators:
    """Testes de let com operadores."""

    @pytest.mark.parametrize("ast,expected", [
        ([token("+"), 1, ["let", "x", 2, "x"]], 3),
        ([token("*"), 2, ["let", "x", 3, "x"]], 6),
        (["let", "x", 2, [token("**"), "x", 3]], 8),
        (["let", "x", [token("-"), 5], "x"], -5),
    ])
    def test_let_with_operators(self, eval_ast, env, ast, expected):
        assert eval_ast(ast, env) == expected


class TestLetEvalErrorPropagation:
    """Testes de propagação de erros em let."""

    def test_error_in_binding(self, eval_ast, env):
        ast = ["let", "x", [token("/"), 1, 0], "x"]
        result = eval_ast(ast, env)
        assert_error(result, "divisão por zero")

    def test_error_in_body(self, eval_ast, env):
        ast = ["let", "x", 1, [token("/"), "x", 0]]
        result = eval_ast(ast, env)
        assert_error(result, "divisão por zero")

    def test_error_in_outer_env(self, eval_ast):
        ast = "x"
        env = {"x": Erro("RUNTIME: erro externo")}
        assert eval_ast(ast, env) == Erro("RUNTIME: erro externo")


class TestLetEvalVariableNames:
    """Testes com diferentes formatos de nomes de variáveis."""

    @pytest.mark.parametrize("name,value", [
        ("x_1", 10),
        ("x1", 20),
        ("variavel_longa", 30),
        ("_private", 40),
        ("x2y3", 50),
    ])
    def test_various_names(self, eval_ast, env, name, value):
        ast = ["let", name, value, name]
        assert eval_ast(ast, env) == value