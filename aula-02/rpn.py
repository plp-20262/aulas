OPERADORES = {"+", "*", "-", "/"}

OPERACAO = {
    "+": lambda a, b: a + b,
    "*": lambda a, b: a * b,
    "-": lambda a, b: a - b,
    "/": lambda a, b: a / b,
}

def tokenizador(programa: str) -> list[str]:
    tokens = programa.split()
    for tok in tokens:
        if not(tok.isdigit() or tok in OPERADORES):
            raise Exception("LÉXICO")
    return tokens


def parser(tokens: list[str]) -> list[str]:
    sim_pilha = []
    for tok in tokens:
        if tok.isdigit():
            sim_pilha.append(tok)

        elif tok in OPERADORES:
            if len(sim_pilha) < 2:
                raise Exception("ERRO SINTÁTICO: operador sem operandos suficiente")
            sim_pilha.pop()
            sim_pilha.pop()
            sim_pilha.append(0)

    if len(sim_pilha) > 1:
        raise Exception("ERRO SINTÁTICO: operandos em excesso")

    return tokens


def interpretador(programa_validado: list[str]) -> str:
    pilha = []
    for tok in programa_validado:
        if tok.isdigit():
            pilha.append(tok)

        elif tok in OPERADORES:
            operador = tok
            arg2 = pilha.pop()
            arg1 = pilha.pop()
            operacao = OPERACAO[operador]
            try:
                res = operacao(int(arg1), int(arg2))
            except ZeroDivisionError:
                raise Exception("ERRO de RUNTIME: divisão por zero")
            pilha.append(res)

    #print(">>>", pilha)
    significado = pilha.pop()
    return significado


def main():
    programa = input("rpn? ")

    tokens = tokenizador(programa)
    programa_validado = parser(tokens)
    significado = interpretador(programa_validado)

    print(f"{programa}   -->   {significado}")


main()
