from tipos import Ast, Erro, monadic_error, Token, TokenType
from lexer import tokenizador
from parser import parser

# tabela de operações da linguagem
OPERACAO = {
    "+": lambda a, b: a + b,
    "*": lambda a, b: a * b,
    "-": lambda a, b: a - b,
    "/": lambda a, b: a / b,
    "?": lambda: int(input()),
    "**": lambda a, b: a ** b,
    "u+": lambda a: a,
    "u-": lambda a: -a,
}


def lifted(op):
    def wrapper(*args):
        for a in args:
            if isinstance(a, Erro):
                return a
        try:
            return op(*args)
        except ZeroDivisionError:
            return Erro("RUNTIME: divisão por zero")
        except Exception:
            return Erro("RUNTIME: erro na operação")
    return wrapper


type Environment = dict[str, int | float]


@monadic_error
def eval(ast: Ast, env: Environment) -> int | float | Erro:
    if isinstance(ast, int):
        return ast

    if isinstance(ast, Token) and ast.type == TokenType.INPUT:
        return int(input())

    if not isinstance(ast, list):
        return Erro(f"RUNTIME: forma de AST inválida '{ast}'")

    if len(ast) == 2:
        op_token, expr = ast[0], ast[1]
        if not isinstance(op_token, Token) or op_token.type not in (TokenType.ADD, TokenType.SUB):
            return Erro(f"RUNTIME: operador unário inválido '{op_token}'")
        v = eval(expr, env)
        if isinstance(v, Erro):
            return v
        operador = "u+" if op_token.type == TokenType.ADD else "u-"
        return lifted(OPERACAO[operador])(v)

    if len(ast) == 3:
        op_token, e1, e2 = ast[0], ast[1], ast[2]
        if not isinstance(op_token, Token):
            return Erro(f"RUNTIME: operador inválido '{op_token}'")
        v1 = eval(e1, env)
        if isinstance(v1, Erro):
            return v1
        v2 = eval(e2, env)
        if isinstance(v2, Erro):
            return v2
        operador = op_token.lexema
        if operador not in OPERACAO:
            return Erro(f"RUNTIME: operador desconhecido '{operador}'")
        return lifted(OPERACAO[operador])(v1, v2)

    return Erro(f"RUNTIME: forma de AST inválida '{ast}'")


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
