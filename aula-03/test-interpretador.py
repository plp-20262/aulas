from mlisp import interpretador

# literais
assert interpretador(0) == 0
assert interpretador(42) == 42

# aritmética básica
assert interpretador(["+", 1, 2]) == 3
assert interpretador(["-", 5, 3]) == 2
assert interpretador(["*", 4, 3]) == 12
assert interpretador(["/", 10, 2]) == 5

# subexpressões
assert interpretador(["+", 1, ["*", 2, 3]]) == 7
assert interpretador(["*", ["+", 1, 2], ["+", 3, 4]]) == 21
assert interpretador(["-", ["+", 5, 5], ["/", 8, 4]]) == 8

# divisão por zero
assert interpretador(["/", 1, 0]) == "ERRO de RUNTIME: divisão por zero"
assert interpretador(["+", 1, ["/", 1, 0]]) == "ERRO de RUNTIME: divisão por zero"

print("Todos os testes passaram!")
