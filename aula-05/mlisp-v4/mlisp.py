from collections.abc import Iterator

import re

from tipos import Ast, Erro, monadic_error, Stream

# tabela de operações da linguagem
OPERACAO = {
    "+": lambda *args: sum(args),
    "*": lambda a, b: a * b,
    "-": lambda *args: -args[0] if len(args) == 1 else args[0] - args[1],
    "/": lambda a, b: a / b,
    "?": lambda : int(input()),
}

# lexer
LPAREN = lambda tok: tok == "("
RPAREN = lambda tok: tok == ")"
INTEIRO = lambda tok: tok and re.fullmatch(r"[0-9]+", tok) is not None
OPERADORES = set(OPERACAO.keys())
OPERADORES_STR = ''.join(sorted(OPERADORES, key=lambda c: c == '-'))  # '-' no fim
OPERADOR = lambda tok: tok and re.fullmatch(rf"[{OPERADORES_STR}]", tok)


def tokenizador(programa: str) -> list[str] | Erro:
    tokens = programa.split()
    for tok in tokens:
        if not(tok.isdigit() or tok in OPERADORES or tok in '()'):
            return Erro(f"erro léxico: token desconhecido {tok}")
    return tokens


# parser
@monadic_error
def parser(tokens: list[str]) -> Ast | Erro:
    stream = Stream(tokens)
    erro = ast = parse_s_expressao(stream)

    if isinstance(erro, Erro):
        return erro

    # se ainda há tokens no stream, é erro
    if stream.peek() is not None:
        return Erro("sintaxe: tokens depois da s-expressão")

    return ast


def parse_s_expressao(stream: Stream) -> Ast | Erro:
    """<s-expressao> ::= LPAREN OPERADOR { INTEIRO | <s-expressao> } RPAREN"""

    # expect(LPAREN)
    if not LPAREN(stream.next()):
        return Erro("sintaxe: falta '('")

    # op = expect(OPERADOR)
    if not OPERADOR(op := stream.next()):
        return Erro("sintaxe: falta OPERADOR")

    args = []
    while not RPAREN(stream.peek()):
        if LPAREN(stream.peek()):
            args.append(parse_s_expressao(stream))
        else:
            # args.append(expect(INTEIRO))
            if not INTEIRO(inteiro := stream.next()):
                return Erro("sintaxe: falta s-expressão ou ')'")
            args.append(int(inteiro))

    # ATENÇÃO: o código abaixo é morto! 
    # O mantenho por ser código defensivo e por ser documentação!
    # expect(RPAREN)
    if not RPAREN(stream.next()):
        return Erro("sintaxe: falta ')'")

    return [op, *args]


# analisador semântico
@monadic_error
def interpretador(ast: Ast) -> int | float | Erro:
    if isinstance(ast, int):
        return ast

    # argumentos
    args = [interpretador(e) for e in ast[1:]]
    for erro in args:
        if isinstance(erro, Erro):
            return erro

    # operação
    operador = str(ast[0])
    operacao = OPERACAO[operador]
    try:
        significado = operacao(*args)
    except ZeroDivisionError:
        return Erro("RUNTIME: divisão por zero")
    return significado


def main():
    programa = input("mlisp? ")

    tokens = tokenizador(preprocessa(programa))
    ast = parser(tokens)
    significado = interpretador(ast)

    print(f"{programa}   -->   {significado}")


def preprocessa(linha: str) -> str:
    linha = linha.replace("(", " ( ")
    linha = linha.replace(")", " ) ")
    return linha


if __name__ == "__main__":
    main()
