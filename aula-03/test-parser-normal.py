from mlisp import parser

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
