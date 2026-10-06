from lexer import tokenizador
from parser import parser
from test_helpers import token

# --- 1. LET BÁSICO ---

# let simples
tokens = tokenizador("let x = 1 in x")
resultado = parser(tokens)
assert resultado == ["let", "x", 1, "x"], f"Obtive {resultado!r}"

# let com expressão aritmética na vinculação
tokens = tokenizador("let x = 1 + 2 in x")
resultado = parser(tokens)
assert resultado == ["let", "x", [token("+"), 1, 2], "x"], f"Obtive {resultado!r}"

# let com expressão aritmética no corpo
tokens = tokenizador("let x = 1 in x + 2")
resultado = parser(tokens)
assert resultado == ["let", "x", 1, [token("+"), "x", 2]], f"Obtive {resultado!r}"

# --- 2. LET ANINHADO ---

# let aninhado simples
tokens = tokenizador("let x = 1 in let y = 2 in x + y")
resultado = parser(tokens)
assert resultado == ["let", "x", 1, ["let", "y", 2, [token("+"), "x", "y"]]], f"Obtive {resultado!r}"

# let aninhado com shadowing
tokens = tokenizador("let x = 1 in let x = 2 in x")
resultado = parser(tokens)
assert resultado == ["let", "x", 1, ["let", "x", 2, "x"]], f"Obtive {resultado!r}"

# --- 3. PRECEDÊNCIA ---

# let tem precedência mais baixa que operadores aditivos no corpo
# let x = 1 in x + 2  ==  let x = 1 in (x + 2)
tokens = tokenizador("let x = 1 in x + 2")
resultado = parser(tokens)
assert resultado == ["let", "x", 1, [token("+"), "x", 2]], f"Obtive {resultado!r}"

# let x = 1 + 2 in x  ==  let x = (1 + 2) in x
tokens = tokenizador("let x = 1 + 2 in x")
resultado = parser(tokens)
assert resultado == ["let", "x", [token("+"), 1, 2], "x"], f"Obtive {resultado!r}"

# let em expressão maior
tokens = tokenizador("1 + let x = 2 in x * 3")
resultado = parser(tokens)
assert resultado == [token("+"), 1, ["let", "x", 2, [token("*"), "x", 3]]], f"Obtive {resultado!r}"

# --- 4. VARIÁVEIS ---

# variável simples
tokens = tokenizador("x")
resultado = parser(tokens)
assert resultado == "x", f"Obtive {resultado!r}"

# variável em expressão
tokens = tokenizador("x + y")
resultado = parser(tokens)
assert resultado == [token("+"), "x", "y"], f"Obtive {resultado!r}"

# variável com operadores unários
tokens = tokenizador("-x")
resultado = parser(tokens)
assert resultado == [token("-"), "x"], f"Obtive {resultado!r}"

# variável com exponenciação
tokens = tokenizador("x ** 2")
resultado = parser(tokens)
assert resultado == [token("**"), "x", 2], f"Obtive {resultado!r}"

# --- 5. EXPRESSÕES COMPLEXAS ---

# let com parênteses
tokens = tokenizador("let x = (1 + 2) in x")
resultado = parser(tokens)
assert resultado == ["let", "x", [token("+"), 1, 2], "x"], f"Obtive {resultado!r}"

# let com unário na vinculação
tokens = tokenizador("let x = -5 in x")
resultado = parser(tokens)
assert resultado == ["let", "x", [token("-"), 5], "x"], f"Obtive {resultado!r}"

# let com INPUT (se suportado)
# tokens = tokenizador("let x = ? in x")
# resultado = parser(tokens)
# assert resultado == ["let", "x", token("?"), "x"], f"Obtive {resultado!r}"

print("Todos os testes de LET bem-formados passaram com sucesso!")