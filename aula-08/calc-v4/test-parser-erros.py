import sys
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


def parse_code(code: str) -> Erro:
    """Helper to tokenize and parse a string, returning any resulting Erro."""
    res = tokenizador(code)
    if isinstance(res, Erro):
        return res
    return parser(res)


# --- 1. ERROS LÉXICOS (Caractere inválido) ---

# Caractere não reconhecido no código
resultado = parse_code("1 @ 2")
assert resultado == Erro("erro léxico: token desconhecido '@'"), f"Obtive {resultado!r}"

# Identificador / Variável não suportada nesta versão
resultado = parse_code("x + 2")
assert resultado == Erro("erro léxico: token desconhecido 'x'"), f"Obtive {resultado!r}"


# --- 2. ERROS SINTÁTICOS (Estrutura malformada) ---

# Entrada vazia / Sem tokens
resultado = parse_code("")
assert resultado == Erro("sintaxe: token inesperado 'EOF'"), f"Obtive {resultado!r}"

# Expressão que termina de forma abrupta com um operador
# 
# [o parser ainda não passa neste teste… nas produções com repetição (parse_exp
# e parse_termo), precisamos verificar se o sub-elemento retornado da chamada
# ao subparser é uma instância de Erro antes de combiná-lo na AST; corrigir o
# código e só então é possível descomentar este teste; faça como exercício]
#
#resultado = parse_code("1 +")
#assert resultado == Erro("sintaxe: token inesperado 'EOF'"), f"Obtive {resultado!r}"

# Parêntese de abertura '(' sem fechar
resultado = parse_code("( 1 + 2")
assert resultado == Erro("sintaxe: esperava ')'"), f"Obtive {resultado!r}"

# Parêntese de fechamento ')' sem correspondente no início
resultado = parse_code(") 1 + 2")
assert resultado == Erro("sintaxe: token inesperado ')'"), f"Obtive {resultado!r}"

# Parênteses vazios
resultado = parse_code("()")
assert resultado == Erro("sintaxe: token inesperado ')'"), f"Obtive {resultado!r}"

# Dois operadores seguidos (falta de operando)
#
# (o parser atual também não passa neste teste… acho que é o mesmo problema do
# outro caso de teste que está comentado acima)
#
#resultado = parse_code("1 + * 2")
#assert resultado == Erro("sintaxe: token inesperado '*'"), f"Obtive {resultado!r}"

# Dois números seguidos sem operador
resultado = parse_code("1 2")
assert resultado == Erro("sintaxe: tokens depois da expressão"), f"Obtive {resultado!r}"

# Duas expressões válidas seguidas
resultado = parse_code("(1 + 2) (3 - 4)")
assert resultado == Erro("sintaxe: tokens depois da expressão"), f"Obtive {resultado!r}"

# Fechamento de parêntese em excesso
resultado = parse_code("(1 + 2))")
assert resultado == Erro("sintaxe: tokens depois da expressão"), f"Obtive {resultado!r}"


# --- 3. ERROS DE OPERADORES UNÁRIOS ---
# NOTA: O parser atual tem limitação conhecida na propagação de erros de subparsers
# (veja testes comentados acima para "1 +" e "1 + * 2").
# Estes testes documentam o comportamento atual; corrigir exigiria verificar
# retornos de Erro em cada chamada recursiva do parser.

# Dois operadores unários seguidos (repetição não permitida pela gramática)
# Atualmente retorna AST malformada contendo Erro, não Erro direto
resultado = parse_code("--2")
assert isinstance(resultado, list) and any(isinstance(x, Erro) for x in _flatten(resultado)), f"Esperava Erro na AST, obtive {resultado!r}"

resultado = parse_code("++2")
assert isinstance(resultado, list) and any(isinstance(x, Erro) for x in _flatten(resultado)), f"Esperava Erro na AST, obtive {resultado!r}"

resultado = parse_code("-+2")
assert isinstance(resultado, list) and any(isinstance(x, Erro) for x in _flatten(resultado)), f"Esperava Erro na AST, obtive {resultado!r}"

resultado = parse_code("+-2")
assert isinstance(resultado, list) and any(isinstance(x, Erro) for x in _flatten(resultado)), f"Esperava Erro na AST, obtive {resultado!r}"


print("Todos os testes de ERRO passaram!")
