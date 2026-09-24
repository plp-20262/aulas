from tipos import Erro
from mlisp import parser
import sys

# lista de tokens vazia
resultado = parser([])
assert resultado == Erro("sintaxe: falta '('")

# ')' sem '(' correspondente
resultado = parser([")"])
assert resultado == Erro("sintaxe: falta '('")

# '(' sem ')' correspondente
resultado = parser(["(", "+", "1", "2"])
assert resultado == Erro("sintaxe: falta s-expressão ou ')'")

# token fora de qualquer parênteses
resultado = parser(["1", "2"])
assert resultado == Erro("sintaxe: falta '('")

# duas expressões coladas: token inesperado após o fim da expressão
resultado = parser(["(", "+", "1", "2", ")", "(", "+", "3", "4", ")"])
assert resultado == Erro("sintaxe: tokens depois da s-expressão")

# parênteses aninhados de forma desbalanceada: fecha um nível a mais
resultado = parser(["(", "+", "1", "2", ")", ")"])
assert resultado == Erro("sintaxe: tokens depois da s-expressão")

# s-expressões não iniciadas por operador
resultado = parser(["(", "(", "+", "1", "2", ")", ")"])
assert resultado == Erro("sintaxe: falta OPERADOR")

# s-expressão vazia
resultado = parser(["(", ")"])
assert resultado == Erro("sintaxe: falta OPERADOR")

# s-expressão com um único valor 
resultado = parser(["(", "1", ")"])
assert resultado == Erro("sintaxe: falta OPERADOR")

print("Todos os testes de ERRO passaram!")
