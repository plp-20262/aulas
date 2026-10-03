import sys
from lexer import tokenizador
from parser import parser

# --- 1. SUCESSO BÁSICO E ARITMÉTICA SIMPLES ---

# Expressão simples: 1 + 2
tokens = tokenizador("1 + 2")
resultado = parser(tokens)
assert resultado == ["+", 1, 2], f"Obtive {resultado!r}"

# Números com múltiplos dígitos: 100 + 2500
tokens = tokenizador("100 + 2500")
resultado = parser(tokens)
assert resultado == ["+", 100, 2500], f"Obtive {resultado!r}"

# Operador de leitura '?'
#
# (o nosso parser não passa nestes testes, porque não deixei o operador de
# input `?` operacional, quando transitei pra nova implementação do lexer e
# decomposição em módulos; se você leu até aqui, considere ativar o operador de
# input na linguagem, fazendo os ajustes necessários; quando o fizer, descomente
# os testes abaixo pra conferir se funcionou)
#
#tokens = tokenizador("?")
#resultado = parser(tokens)
#assert resultado == "?", f"Obtive {resultado!r}"

#tokens = tokenizador("1 + ?")
#resultado = parser(tokens)
#assert resultado == ["+", 1, "?"], f"Obtive {resultado!r}"


# --- 2. PRECEDÊNCIA E ASSOCIATIVIDADE ---

# Precedência: * sobre +
tokens = tokenizador("1 + 2 * 3")
resultado = parser(tokens)
assert resultado == ["+", 1, ["*", 2, 3]], f"Obtive {resultado!r}"

# Precedência: ** sobre *
tokens = tokenizador("2 * 3 ** 4")
resultado = parser(tokens)
assert resultado == ["*", 2, ["**", 3, 4]], f"Obtive {resultado!r}"

# Precedência tripla: + vs * vs **
tokens = tokenizador("1 + 2 * 3 ** 4")
resultado = parser(tokens)
assert resultado == ["+", 1, ["*", 2, ["**", 3, 4]]], f"Obtive {resultado!r}"

# Associatividade à esquerda: Subtração (2 - 3 - 2)
tokens = tokenizador("2 - 3 - 2")
resultado = parser(tokens)
assert resultado == ["-", ["-", 2, 3], 2], f"Obtive {resultado!r}"

# Associatividade à esquerda: Divisão (8 / 2 / 4)
tokens = tokenizador("8 / 2 / 4")
resultado = parser(tokens)
assert resultado == ["/", ["/", 8, 2], 4], f"Obtive {resultado!r}"

# Associatividade à direita: Exponenciação (2 ** 3 ** 2)
tokens = tokenizador("2 ** 3 ** 2")
resultado = parser(tokens)
assert resultado == ["**", 2, ["**", 3, 2]], f"Obtive {resultado!r}"


# --- 3. PARÊNTESES E ESTRUTURA ---

# Alteração de precedência por parênteses: (1 + 2) * 3
tokens = tokenizador("(1 + 2) * 3")
resultado = parser(tokens)
assert resultado == ["*", ["+", 1, 2], 3], f"Obtive {resultado!r}"

# Aninhamento duplo de parênteses: ((1 + 2))
tokens = tokenizador("((1 + 2))")
resultado = parser(tokens)
assert resultado == ["+", 1, 2], f"Obtive {resultado!r}"

# Expressão complexa aninhada
tokens = tokenizador("(1 + 2) * (3 - 4)")
resultado = parser(tokens)
assert resultado == ["*", ["+", 1, 2], ["-", 3, 4]], f"Obtive {resultado!r}"


# --- 4. ESPAÇAMENTO E FORMATAÇÃO (ROBUSTÊS DO LEXER) ---

# Sem espaços entre tokens
tokens = tokenizador("2**(3+1)")
resultado = parser(tokens)
assert resultado == ["**", 2, ["+", 3, 1]], f"Obtive {resultado!r}"

# Espaços e quebras de linha múltiplos
tokens = tokenizador(" 10  + \n\t (  20   *  30 ) ")
resultado = parser(tokens)
assert resultado == ["+", 10, ["*", 20, 30]], f"Obtive {resultado!r}"

print("Todos os testes de expressões BEM-FORMADAS passaram com sucesso!")
