from tipos import Erro
from aljabr import eval, Environment
from test_helpers import token

# Ambiente padrão (vazio)
env: Environment = {}

# --- 1. VARIÁVEIS SIMPLES ---

# Lookup de variável existente
assert eval("x", {"x": 5}) == 5

# Lookup de variável com valor float
assert eval("x", {"x": 3.14}) == 3.14

# Lookup de variável com valor Erro (ambiente lifted)
assert eval("x", {"x": Erro("RUNTIME: teste")}) == Erro("RUNTIME: teste")

# Variável não vinculada
assert eval("x", {}) == Erro("RUNTIME: variável 'x' não vinculada")
assert eval("y", {"x": 1}) == Erro("RUNTIME: variável 'y' não vinculada")

# --- 2. LET BÁSICO ---

# let simples: let x = 1 in x
assert eval(["let", "x", 1, "x"], env) == 1

# let com expressão na vinculação: let x = 1 + 2 in x
assert eval(["let", "x", [token("+"), 1, 2], "x"], env) == 3

# let com expressão no corpo: let x = 1 in x + 2
assert eval(["let", "x", 1, [token("+"), "x", 2]], env) == 3

# let com multiplicação no corpo: let x = 2 in x * 3
assert eval(["let", "x", 2, [token("*"), "x", 3]], env) == 6

# --- 3. LET ANINHADO ---

# let aninhado simples
assert eval(["let", "x", 1, ["let", "y", 2, [token("+"), "x", "y"]]], env) == 3

# Shadowing: let x = 1 in let x = 2 in x
assert eval(["let", "x", 1, ["let", "x", 2, "x"]], env) == 2

# Variável externa ainda acessível se não sombreada
assert eval(["let", "x", 1, ["let", "y", 2, [token("+"), "x", "y"]]], env) == 3

# --- 4. LET COM OPERADORES ---

# let em expressão aditiva: 1 + let x = 2 in x
assert eval([token("+"), 1, ["let", "x", 2, "x"]], env) == 3

# let em multiplicação: 2 * let x = 3 in x
assert eval([token("*"), 2, ["let", "x", 3, "x"]], env) == 6

# let com exponenciação: let x = 2 in x ** 3
assert eval(["let", "x", 2, [token("**"), "x", 3]], env) == 8

# let com unário: let x = -5 in x
assert eval(["let", "x", [token("-"), 5], "x"], env) == -5

# --- 5. PROPAGAÇÃO DE ERROS ---

# Erro na expressão de vinculação propaga
assert eval(["let", "x", [token("/"), 1, 0], "x"], env) == Erro("RUNTIME: divisão por zero")

# Erro no corpo propaga
assert eval(["let", "x", 1, [token("/"), "x", 0]], env) == Erro("RUNTIME: divisão por zero")

# Erro no ambiente externo propaga
assert eval("x", {"x": Erro("RUNTIME: erro externo")}) == Erro("RUNTIME: erro externo")

# --- 6. VARIÁVEIS COM NOMES DIFERENTES ---

# Nomes com underscore
assert eval(["let", "x_1", 10, "x_1"], env) == 10

# Nomes com dígitos
assert eval(["let", "x1", 20, "x1"], env) == 20

# Nomes longos
assert eval(["let", "variavel_longa", 30, "variavel_longa"], env) == 30

print("Todos os testes do interpretador com LET passaram com sucesso!")