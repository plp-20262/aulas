from m2lisp import parser

# + variádico teste 1: (+ 1 2 3 4) -> ['+', 1, 2, 3, 4]
resultado = parser(["(", "+", "1", "2", "3", "4", ")"])
assert resultado == ["+", 1, 2, 3, 4], f"esperava ['+', 1, 2, 3, 4], obtive {resultado!r}"

# + variádico teste 2: (+ 5) -> ['+', 1]
resultado = parser(["(", "+", "5", ")"])
assert resultado == ["+", 5], f"esperava ['+', 5], obtive {resultado!r}"

# + variádico teste 3: (+) -> ['+']
resultado = parser(["(", "+", ")"])
assert resultado == ["+"], f"esperava ['+'], obtive {resultado!r}"

# - unário: (- 5) -> ['-', '5']
resultado = parser(["(", "-", "5", ")"])
assert resultado == ["-", 5], f"esperava ['-', 5], obtive {resultado!r}"

#########
# abaixo os testes originais

# expressão simples: (+ 1 2) -> ['+', 1, 2]
resultado = parser(["(", "+", "1", "2", ")"])
assert resultado == ["+", 1, 2], f"esperava ['+', 1, 2], obtive {resultado!r}"

# expressão aninhada: (+ 1 (* 2 3)) -> ['+', 1, ['*', 2, 3]]
resultado = parser(["(", "+", "1", "(", "*", "2", "3", ")", ")"])
assert resultado == ["+", 1, ["*", 2, 3]], f"obtive {resultado!r}"

# operador com um único operando: (- 5)
resultado = parser(["(", "-", "5", ")"])
assert resultado == ["-", 5], f"obtive {resultado!r}"

# aninhamento em ambos os operandos: (* (+ 1 2) (- 3 4))
resultado = parser(["(", "*", "(", "+", "1", "2", ")", "(", "-", "3", "4", ")", ")"])
assert resultado == ["*", ["+", 1, 2], ["-", 3, 4]], f"obtive {resultado!r}"

print("Todos os testes NORMAIS passaram!")
