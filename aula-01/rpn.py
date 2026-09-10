def tokenizador(programa: str) -> list[str]:
    tokens = programa.split()
    for tok in tokens:
        if not(tok.isdigit() or tok == '+'):
            raise Exception("RPN: ERRO LÉXICO")
    return tokens


def parser(tokens: list[str]) -> list[str]:
    sim_pilha = []
    for tok in tokens:
        if tok.isdigit():
            sim_pilha.append(tok)
        elif tok == '+':
            if len(sim_pilha) < 2:
                raise Exception("RPN: ERRO SINTÁTICO: operador sem operandos suficiente")
            sim_pilha.pop()
            sim_pilha.pop()
            sim_pilha.append(0)

    if len(sim_pilha) > 1:
        raise Exception("ERRO SINTÁTICO: operandos em execsso")

    return tokens


def interpretador(programa: str) -> str:
    tokens = tokenizador(programa)
    tokens_ok = parser(tokens)
    pilha = []
    for tok in tokens_ok:
        if tok.isdigit():
            pilha.append(tok)
        elif tok == '+':
            arg2 = pilha.pop()
            arg1 = pilha.pop()
            res = int(arg1) + int(arg2)
            pilha.append(res)

    significado = pilha.pop()
    return significado


def main():
    programa = input("rpn? ")
    significado = interpretador(programa)
    print(f"{programa}   -->   {significado}")


main()
