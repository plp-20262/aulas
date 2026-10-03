from tipos import Erro
from calc import eval, Environment

# Ambiente padrão (vazio) para a calc-v2
env: Environment = {}

# 1. Literais
assert eval(0, env) == 0
assert eval(42, env) == 42

# 2. Operadores Binários Básicos (Regra Op)
assert eval(["+", 1, 2], env) == 3
assert eval(["-", 5, 3], env) == 2
assert eval(["*", 4, 3], env) == 12
assert eval(["/", 10, 2], env) == 5
assert eval(["**", 2, 3], env) == 8

# 3. Subexpressões Aninhadas (Composicionalidade)
assert eval(["+", 1, ["*", 2, 3]], env) == 7
assert eval(["*", ["+", 1, 2], ["+", 3, 4]], env) == 21
assert eval(["-", ["+", 5, 5], ["/", 8, 4]], env) == 8

# 4. Divisão por Zero (Regra DivZero)
assert eval(["/", 1, 0], env) == Erro("RUNTIME: divisão por zero")

# 5. Propagação de Erros (Regras ErrEsq e ErrDir)
assert eval(["+", ["/", 1, 0], 2], env) == Erro("RUNTIME: divisão por zero")  # ErrEsq
assert eval(["+", 1, ["/", 1, 0]], env) == Erro("RUNTIME: divisão por zero")  # ErrDir
assert eval(["*", ["/", 5, 0], ["+", 2, 3]], env) == Erro("RUNTIME: divisão por zero")

# 6. Validação de Formato da AST (Nós malformados)
assert isinstance(eval(["+"], env), Erro)  # Faltam operandos
assert isinstance(eval(["+", 1], env), Erro)  # Operador binário com apenas 1 operando
assert isinstance(eval(["+", 1, 2, 3], env), Erro)  # Mais operandos do que o nó binário suporta

print("Todos os testes passaram com sucesso!")
