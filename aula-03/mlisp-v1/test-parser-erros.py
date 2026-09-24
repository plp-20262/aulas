from mlisp import parser

# lista de tokens vazia
resultado = parser([])
assert resultado.startswith("ERRO")

# ')' sem '(' correspondente
resultado = parser([")"])
assert resultado.startswith("ERRO")

# '(' sem ')' correspondente
resultado = parser(["(", "+", "1", "2"])
assert resultado.startswith("ERRO")

# token fora de qualquer parênteses
resultado = parser(["1", "2"])
assert resultado.startswith("ERRO")

# duas expressões coladas: token inesperado após o fim da expressão
resultado = parser(["(", "+", "1", "2", ")", "(", "+", "3", "4", ")"])
assert resultado.startswith("ERRO")

# parênteses aninhados de forma desbalanceada: fecha um nível a mais
resultado = parser(["(", "+", "1", "2", ")", ")"])
assert resultado.startswith("ERRO")

# s-expressões não iniciadas por operador
resultado = parser(["(", "(", "+", "1", "2", ")", ")"])
assert resultado.startswith("ERRO")

# s-expressão vazia
resultado = parser(["(", ")"])
assert resultado.startswith("ERRO")

# s-expressão com um único valor 
resultado = parser(["(", "1", ")"])
assert resultado.startswith("ERRO")

print("Todos os testes de ERRO passaram!")
