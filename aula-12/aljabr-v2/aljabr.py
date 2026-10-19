import sys
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


# Implementa f_op↑: propaga Erro e trata operações indefinidas,
# como div por zero, por exemplo. Ver "Operações Semânticas"
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


# Define o tipo de ambiente `ρ: Var ⇀ Val`. Relembre que especificamos
# que `Val = ℝ ∪ {erro}` (versão lifted, com suporte a erros).
type Environment = dict[str, int | float | Erro]


@monadic_error
def eval(ast: Ast, env: Environment) -> int | float | Erro:
    # Regra (Num): ⟨n, ρ⟩ ⇓ n
    if isinstance(ast, int):
        return ast

    # Regras: 
    # (Var): ρ(x)=v ⇒ ⟨x,ρ⟩⇓v; 
    # (VarNaoLigada): x∉dom(ρ) ⇒ ⟨x,ρ⟩⇓erro
    if isinstance(ast, str):
        if ast in env:
            return env[ast]
        return Erro(f"RUNTIME: variável '{ast}' não vinculada")

    if isinstance(ast, Token) and ast.type == TokenType.INPUT:
        return int(input())

    # AST malformada: nó não é lista (verifica aridade inválida)
    if not isinstance(ast, list):
        return Erro(f"RUNTIME: forma de AST inválida '{ast}'")

    # Regra (Let): ⟨let x=e1 in e2, ρ⟩ ⇓ v2, onde ⟨e1,ρ⟩⇓v1 e ⟨e2,ρ[x↦v1]⟩⇓v2
    # {**env, var: v1} cria novo dicionário (ρ[x↦v1] é nova função, não muta ρ)
    if len(ast) == 4 and ast[0] == "let":
        _, var, e1, e2 = ast
        v1 = eval(e1, env)
        if isinstance(v1, Erro):
            return v1
        new_env = {**env, var: v1}
        return eval(e2, new_env)

    # Operador unário: aplica (Op) com f_op↑, ver "Operações Aritméticas"
    if len(ast) == 2:
        op_token, expr = ast[0], ast[1]
        if not isinstance(op_token, Token) or op_token.type not in (TokenType.ADD, TokenType.SUB):
            return Erro(f"RUNTIME: operador unário inválido '{op_token}'")
        v = eval(expr, env)
        if isinstance(v, Erro):
            return v
        operador = "u+" if op_token.type == TokenType.ADD else "u-"
        return lifted(OPERACAO[operador])(v)

    # Regra (Op) binário: ⟨e1 Op e2, ρ⟩ ⇓ v,
    # onde ⟨e1,ρ⟩⇓v1, ⟨e2,ρ⟩⇓v2, f_Op↑(v1,v2) = v
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

    # AST com aridade não suportada (1, 2, 3 elementos já tratados; >3 ou 0 é erro)
    return Erro(f"RUNTIME: forma de AST inválida '{ast}'")


def main():
    if len(sys.argv) > 1:
        programa = open(sys.argv[1]).read()
    else:
        programa = sys.stdin.read()

    tokens = tokenizador(programa)
    ast = parser(tokens)
    
    # O ambiente ρ inicia vazio para aljabr
    env: Environment = {}
    significado = eval(ast, env)

    print(f"{programa}")
    print(f"-->  {significado}")


if __name__ == "__main__":
    main()
