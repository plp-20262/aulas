from tipos import Erro
from aljabr import eval, Environment
from test_helpers import token

# Ambiente padrão (vazio) para a calc-v2
env: Environment = {}

# 1. Literais
assert eval(0, env) == 0
assert eval(42, env) == 42

# 2. Operadores Binários Básicos (Regra Op)
assert eval([token("+"), 1, 2], env) == 3
assert eval([token("-"), 5, 3], env) == 2
assert eval([token("*"), 4, 3], env) == 12
assert eval([token("/"), 10, 2], env) == 5
assert eval([token("**"), 2, 3], env) == 8

# 3. Subexpressões Aninhadas (Composicionalidade)
assert eval([token("+"), 1, [token("*"), 2, 3]], env) == 7
assert eval([token("*"), [token("+"), 1, 2], [token("+"), 3, 4]], env) == 21
assert eval([token("-"), [token("+"), 5, 5], [token("/"), 8, 4]], env) == 8

# 4. Divisão por Zero (Regra DivZero)
assert eval([token("/"), 1, 0], env) == Erro("RUNTIME: divisão por zero")

# 5. Propagação de Erros (Regras ErrEsq e ErrDir)
assert eval([token("+"), [token("/"), 1, 0], 2], env) == Erro("RUNTIME: divisão por zero")  # ErrEsq
assert eval([token("+"), 1, [token("/"), 1, 0]], env) == Erro("RUNTIME: divisão por zero")  # ErrDir
assert eval([token("*"), [token("/"), 5, 0], [token("+"), 2, 3]], env) == Erro("RUNTIME: divisão por zero")

# 6. Validação de Formato da AST (Nós malformados)
assert isinstance(eval([token("+")], env), Erro)  # Faltam operandos
assert isinstance(eval([token("*"), 1], env), Erro)  # Operador binário com apenas 1 operando
assert isinstance(eval([token("+"), 1, 2, 3], env), Erro)  # Mais operandos do que o nó binário suporta

# 7. Operadores Unários
assert eval([token("+"), 5], env) == 5   # unário plus
assert eval([token("-"), 5], env) == -5  # unário minus
assert eval([token("+"), -3], env) == -3  # unário plus com negativo
assert eval([token("-"), -3], env) == 3   # unário minus com negativo

# 8. Precedência: unário > ** > * / > + -
assert eval([token("+"), [token("**"), 2, 3]], env) == 8   # +(2**3)
assert eval([token("-"), [token("**"), 2, 3]], env) == -8  # -(2**3)
assert eval([token("**"), [token("-"), 2], 3], env) == -8  # (-2)**3
assert eval([token("*"), [token("-"), 3], 4], env) == -12  # -3*4
assert eval([token("+"), [token("-"), 3], 4], env) == 1    # -3+4

# 9. Associatividade à direita de **
assert eval([token("**"), 2, [token("**"), 3, 2]], env) == 512  # 2**(3**2)
assert eval([token("**"), [token("-"), 2], [token("-"), 3]], env) == -0.125  # (-2)**(-3) = 1/(-8)
assert eval([token("**"), 2, [token("-"), 3]], env) == 0.125  # 2**-3 = 1/8

# 10. Erro com INPUT token como expressão (não deveria acontecer no parser, mas testar eval)
# assert isinstance(eval(token("?"), env), Erro)  # INPUT sem contexto

print("Todos os testes passaram com sucesso!")
