from tipos import Ast, Erro, monadic_error, Token, TokenType
from lexer import tokenizador
from parser import parser

# tabela de operações da linguagem
OPERACAO = {
    "+": lambda *args: sum(args),
    "*": lambda a, b: a * b,
    "-": lambda *args: -args[0] if len(args) == 1 else args[0] - args[1],
    "/": lambda a, b: a / b,
    "?": lambda : int(input()),
    "**": lambda a, b: a ** b,
}

type Environment = dict[str, int | float]

@monadic_error
def eval(ast: Ast, env: Environment) -> int | float | Erro:
    # Regra (Num)
    if isinstance(ast, int):
        return ast

    # Regra (Input) - Token INPUT
    if isinstance(ast, Token) and ast.type == TokenType.INPUT:
        return int(input())

    # Estrutura do nó AST fora do esperado
    if not isinstance(ast, list) or len(ast) != 3:
        return Erro(f"RUNTIME: forma de AST inválida '{ast}'")

    # Estrutura do nó AST: [operador, e1, e2]
    operador_token, e1, e2 = ast[0], ast[1], ast[2]

    # Extrai o lexema do operador para lookup na tabela
    if isinstance(operador_token, Token):
        operador = operador_token.lexema
    else:
        return Erro(f"RUNTIME: operador inválido '{operador_token}'")

    # Avalia subexpressões no ambiente env (Premissas)
    v1 = eval(e1, env)
    if isinstance(v1, Erro):  # Regra (ErrEsq)
        return v1

    v2 = eval(e2, env)
    if isinstance(v2, Erro):  # Regra (ErrDir)
        return v2

    # Regra (DivZero)
    if operador == "/" and v2 == 0:
        return Erro("RUNTIME: divisão por zero")

    # Regra (Op)
    operacao = OPERACAO[operador]
    v = operacao(v1, v2)
    return v


def main():
    programa = input("calc? ")

    tokens = tokenizador(programa)
    ast = parser(tokens)
    
    # O ambiente ρ inicia vazio para calc-v2
    env: Environment = {}
    significado = eval(ast, env)

    print(f"{programa}   -->   {significado}")


if __name__ == "__main__":
    main()
