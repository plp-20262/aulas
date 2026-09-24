from typing import Any

from erros import monadic_error, Erro

type Ast = int | str | list[Ast]

OPERADORES = {"+", "*", "-", "/", "(", ")"}

OPERACAO = {
    "+": lambda a, b: a + b,
    "*": lambda a, b: a * b,
    "-": lambda a, b: a - b,
    "/": lambda a, b: a / b,
}

def tokenizador(programa: str) -> list[str] | Erro:
    tokens = programa.split()
    for tok in tokens:
        if not(tok.isdigit() or tok in OPERADORES):
            return "ERRO LÉXICO"
    return tokens


@monadic_error
def parser(tokens: list[str]) -> Ast | Erro:
    pilha = []
    ast: Ast | Erro | None = None

    for tok in tokens:
        if tok == "(":
            novo_node: list[Any] = []
            pilha.append(novo_node)

        elif tok == ")":
            ultimo_node = pilha.pop()
            if len(pilha) > 0:
                pilha[-1].append(ultimo_node)
            else:
                ast = ultimo_node

        else: # número ou operador
            ultimo_node = pilha[-1]
            ultimo_node.append(int(tok) if tok.isdigit() else tok)

    assert ast is not None
    return ast


@monadic_error
def interpretador(ast: Ast) -> int | float | Erro:
    if isinstance(ast, int):
        return ast

    operador = str(ast[0])
    arg1 = interpretador(ast[1])
    arg2 = interpretador(ast[2])
    operacao = OPERACAO[operador]
    try:
        significado = operacao(arg1, arg2)
    except ZeroDivisionError:
        return "ERRO:"
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
