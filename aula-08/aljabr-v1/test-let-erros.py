from tipos import Erro
from lexer import tokenizador
from parser import parser


def _flatten(lst):
    """Helper to recursively find Erro in nested lists."""
    for item in lst:
        if isinstance(item, Erro):
            yield item
        elif isinstance(item, list):
            yield from _flatten(item)


def parse_code(code: str) -> Erro | list:
    """Helper to tokenize and parse a string, returning any resulting Erro."""
    res = tokenizador(code)
    if isinstance(res, Erro):
        return res
    return parser(res)


# --- 1. ERROS SINTÁTICOS (reserved words as identifiers) ---

# 'let' como nome de variável não deve ser permitido (é palavra reservada)
resultado = parse_code("let x = 1 in let")
assert resultado == Erro("sintaxe: esperava nome após 'let'"), f"Obtive {resultado!r}"

# 'in' como nome de variável não deve ser permitido (é palavra reservada)
resultado = parse_code("let x = 1 in in")
assert resultado == Erro("sintaxe: token inesperado 'in'"), f"Obtive {resultado!r}"


# --- 2. ERROS SINTÁTICOS (let malformado) ---

# Falta '=' após nome
resultado = parse_code("let x 1 in x")
assert resultado == Erro("sintaxe: esperava '=' após nome"), f"Obtive {resultado!r}"

# Falta 'in' após expressão de vinculação
resultado = parse_code("let x = 1 x")
assert resultado == Erro("sintaxe: esperava 'in' após expressão de vinculação"), f"Obtive {resultado!r}"

# Falta expressão de vinculação
resultado = parse_code("let x = in x")
assert isinstance(resultado, Erro) and "inesperado" in resultado.msg, f"Obtive {resultado!r}"

# Falta corpo do let
resultado = parse_code("let x = 1 in")
assert isinstance(resultado, Erro) and "inesperado" in resultado.msg, f"Obtive {resultado!r}"

# Falta nome após let
resultado = parse_code("let = 1 in x")
assert resultado == Erro("sintaxe: esperava nome após 'let'"), f"Obtive {resultado!r}"

# let sem nada
resultado = parse_code("let")
assert isinstance(resultado, Erro), f"Obtive {resultado!r}"

# --- 3. ERROS DE VARIÁVEIS ---

# Variável começando com dígito (erro sintático: dois tokens)
resultado = parse_code("1x")
assert resultado == Erro("sintaxe: tokens depois da expressão"), f"Obtive {resultado!r}"

# Variável com maiúscula (erro léxico - não suportado pela regex)
resultado = parse_code("X")
assert resultado == Erro("erro léxico: token desconhecido 'X'"), f"Obtive {resultado!r}"

# --- 4. ERROS DE EXPRESSÕES DENTRO DO LET ---

# Expressão de vinculação malformada (erro propagado na AST)
resultado = parse_code("let x = 1 + in x")
assert isinstance(resultado, list) and any(isinstance(x, Erro) for x in _flatten(resultado)), f"Esperava Erro na AST, obtive {resultado!r}"

# Corpo malformado (erro propagado na AST)
resultado = parse_code("let x = 1 in 1 +")
assert isinstance(resultado, list) and any(isinstance(x, Erro) for x in _flatten(resultado)), f"Esperava Erro na AST, obtive {resultado!r}"

print("Todos os testes de ERRO em LET passaram!")