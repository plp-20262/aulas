import pytest
from tipos import Erro
from tests.conftest import assert_error, token


class TestEvalCore:
    """Testes do avaliador (eval) para expressões centrais."""

    # --- 1. LITERAIS (apenas inteiros; floats surgem como resultado de operações) ---
    @pytest.mark.parametrize("value", [0, 42, -10])
    def test_literals(self, eval_ast, env, value):
        assert eval_ast(value, env) == value

    # --- 2. OPERADORES BINÁRIOS ---
    @pytest.mark.parametrize("op,a,b,expected", [
        ("+", 1, 2, 3),
        ("-", 5, 3, 2),
        ("*", 4, 3, 12),
        ("/", 10, 2, 5),
        ("**", 2, 3, 8),
        # Divisão produz float
        ("/", 7, 2, 3.5),
    ])
    def test_binary_operators(self, eval_ast, env, op, a, b, expected):
        assert eval_ast([token(op), a, b], env) == expected

    # --- 3. SUBEXPRESSÕES ANINHADAS ---
    @pytest.mark.parametrize("ast,expected", [
        ([token("+"), 1, [token("*"), 2, 3]], 7),
        ([token("*"), [token("+"), 1, 2], [token("+"), 3, 4]], 21),
        ([token("-"), [token("+"), 5, 5], [token("/"), 8, 4]], 8),
    ])
    def test_nested_expressions(self, eval_ast, env, ast, expected):
        assert eval_ast(ast, env) == expected

    # --- 4. DIVISÃO POR ZERO ---
    def test_division_by_zero(self, eval_ast, env):
        result = eval_ast([token("/"), 1, 0], env)
        assert_error(result, "divisão por zero")

    # --- 5. PROPAGAÇÃO DE ERROS ---
    @pytest.mark.parametrize("ast", [
        [token("+"), [token("/"), 1, 0], 2],  # ErrEsq
        [token("+"), 1, [token("/"), 1, 0]],  # ErrDir
        [token("*"), [token("/"), 5, 0], [token("+"), 2, 3]],
    ])
    def test_error_propagation(self, eval_ast, env, ast):
        result = eval_ast(ast, env)
        assert_error(result, "divisão por zero")

    # --- 6. VALIDAÇÃO DE FORMATO DA AST ---
    @pytest.mark.parametrize("ast", [
        [token("+")],              # Faltam operandos
        [token("*"), 1],           # Operador binário com 1 operando
        [token("+"), 1, 2, 3],     # Mais operandos que o suportado
    ])
    def test_malformed_ast(self, eval_ast, env, ast):
        result = eval_ast(ast, env)
        assert isinstance(result, Erro)

    # --- 7. OPERADORES UNÁRIOS ---
    @pytest.mark.parametrize("op,value,expected", [
        ("+", 5, 5),      # unário plus
        ("-", 5, -5),     # unário minus
        ("+", -3, -3),    # unário plus com negativo
        ("-", -3, 3),     # unário minus com negativo
    ])
    def test_unary_operators(self, eval_ast, env, op, value, expected):
        assert eval_ast([token(op), value], env) == expected

    # --- 8. PRECEDÊNCIA: unário > ** > * / > + - ---
    @pytest.mark.parametrize("ast,expected", [
        ([token("+"), [token("**"), 2, 3]], 8),     # +(2**3)
        ([token("-"), [token("**"), 2, 3]], -8),    # -(2**3)
        ([token("**"), [token("-"), 2], 3], -8),    # (-2)**3
        ([token("*"), [token("-"), 3], 4], -12),    # -3*4
        ([token("+"), [token("-"), 3], 4], 1),      # -3+4
    ])
    def test_precedence_unary_over_binary(self, eval_ast, env, ast, expected):
        assert eval_ast(ast, env) == expected

    # --- 9. ASSOCIATIVIDADE À DIREITA DE ** ---
    @pytest.mark.parametrize("ast,expected", [
        ([token("**"), 2, [token("**"), 3, 2]], 512),           # 2**(3**2)
        ([token("**"), [token("-"), 2], [token("-"), 3]], -0.125),  # (-2)**(-3)
        ([token("**"), 2, [token("-"), 3]], 0.125),             # 2**-3
    ])
    def test_right_assoc_pow(self, eval_ast, env, ast, expected):
        assert eval_ast(ast, env) == expected


class TestEvalInput:
    """Testes para operador INPUT (?)."""

    # INPUT requer entrada do usuário - não testável automaticamente sem mock
    # Mantido como referência para implementação futura
    pass