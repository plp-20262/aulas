from erros import monadic_error, Erro

OPERADORES = {"+", "*", "-", "/"}

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
def parser(tokens: list[str]) -> list[str] | Erro:
    sim_pilha = []
    for tok in tokens:
        if tok.isdigit():
            sim_pilha.append(tok)

        elif tok in OPERADORES:
            if len(sim_pilha) < 2:
                return "ERRO SINTÁTICO: operador sem operandos suficiente"
            sim_pilha.pop()
            sim_pilha.pop()
            sim_pilha.append(0)

    if len(sim_pilha) > 1:
        return "ERRO SINTÁTICO: operandos em execsso"

    return tokens


@monadic_error
def interpretador(programa_validado: list[str]) -> str | Erro:
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
                return "ERRO de RUNTIME: divisão por zero"
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
