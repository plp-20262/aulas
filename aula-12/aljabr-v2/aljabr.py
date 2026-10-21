import sys
from dataclasses import dataclass
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


# Implementa f_op↑: a definição da §3 —
#   f↑(v1, ..., vn) = erro     se algum v_i = erro        (propagação monádica)
#                      f(...)   se todos ∈ ℝ e f definida
#                      erro     caso contrário (ex.: div por zero, e em v2
#                               também operações sobre closures)
def lifted(op):
    def wrapper(*args):
        for a in args:
            if isinstance(a, Erro):
                return a
        # "caso contrário" do lift (§3): f↑ só está definida sobre ℝ.
        # Com Val incluindo closures, isto cobre `q + 1`, `-q` etc. — sem
        # nenhuma regra nova de avaliação.
        for a in args:
            if not isinstance(a, (int, float)):
                return Erro("RUNTIME: operação sobre valor não numérico")
        try:
            return op(*args)
        except ZeroDivisionError:
            return Erro("RUNTIME: divisão por zero")
        except Exception:
            return Erro("RUNTIME: erro na operação")
    return wrapper


# Define o tipo de ambiente `ρ: Var ⇀ Val`. Relembre que especificamos
# que `Val = ℝ ∪ {erro}` (versão lifted, com suporte a erros).
# aljabr v2 (§3): Val passa a incluir closures, então ρ também pode
# associar nomes a closures (ex.: `let f = fn ... in ...`).
type Environment = dict[str, "Val"]


# aljabr v2 (§3): domínio dos valores
#   Val = ℝ ∪ Clo ∪ {erro}
# com Clo = Var* × Exp × Env — closures são triplas (parâmetros, corpo,
# ambiente de criação), na notação clo((p1, ..., pn), e, ρ).
# Uma dataclass imutável com três campos serve bem (§4.3).
@dataclass(frozen=True)
class Closure:
    params: tuple[str, ...]   # (p1, ..., pn)
    corpo: Ast                # e — o corpo, que NÃO é avaliado na criação
    env: "Environment"        # ρ0 — ambiente de criação, "congelado" pela cópia


# aljabr v2 (§3): Val = ℝ ∪ Clo ∪ {erro}
type Val = int | float | Erro | Closure


@monadic_error
def eval(ast: Ast, env: Environment) -> Val:
    # Regra (Num): ⟨n, ρ⟩ ⇓ n
    if isinstance(ast, int):
        return ast

    # Regras: 
    # (Var): ρ(x)=v ⇒ ⟨x,ρ⟩⇓v; 
    # (VarNaoLigada): x∉dom(ρ) ⇒ ⟨x,ρ⟩⇓erro
    # aljabr v2 (§3): com ambiente lifted, ρ(x)=erro para x∉dom(ρ), o que
    # também faz (Var) devolver closures quando ρ(x) é um closure.
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

    # --- aljabr v2 (§3): regras novas de funções ---
    # Os nós novos têm TAG de string em ast[0] ("fn" e "app"), enquanto os
    # operadores binários/unários têm um Token nessa posição — é por isso
    # que as tags são checadas ANTES dos ramos que decidem por aridade
    # (questão de projeto da §4.2).

    # Regra (Lam): ⟨fn (p1,...,pn) ⇒ e, ρ⟩ ⇓ clo((p1,...,pn), e, ρ)
    # Sem premissas: o corpo NÃO é avaliado; ρ é capturado (congelado por
    # uma cópia — ρ0 não depende de ρ e não é mutada depois).
    if len(ast) == 3 and ast[0] == "fn":
        _, params, corpo = ast
        return Closure(tuple(params), corpo, dict(env))

    # Regras de aplicação. A convenção de propagação de erro da §3 vale
    # aqui: se qualquer premissa ⟨e,ρ⟩ ⇓ v produz erro, o resultado é erro
    # (erros são ESTRICTOS: erro não pode ser passado como argumento).
    if len(ast) == 3 and ast[0] == "app":
        _, e_f, args = ast

        # Premissa 1: ⟨e_f, ρ⟩ ⇓ v_f  (ρ é o ambiente DE CHAMADA)
        v_f = eval(e_f, env)
        if isinstance(v_f, Erro):
            return v_f  # propagação: a regra (App) não se aplica

        # Regra (AppNaoFuncao): v_f ∉ Clo ⇒ erro
        if not isinstance(v_f, Closure):
            return Erro("RUNTIME: aplicação de não-função")

        # Regra (AppAridade): m ≠ n ⇒ erro. ESCOLHA DE PROJEITO (§3): a
        # aridade é verificada ANTES de avaliar os argumentos — por isso
        # as três regras de aplicação são mutuamente exclusivas.
        if len(args) != len(v_f.params):
            return Erro(
                f"RUNTIME: aridade incorreta: esperava {len(v_f.params)} "
                f"argumento(s), recebeu {len(args)}"
            )

        # Premissas 2: ⟨a_i, ρ⟩ ⇓ v_i (argumentos no ambiente de chamada)
        vals: list[Val] = []
        for a in args:
            v = eval(a, env)
            if isinstance(v, Erro):
                return v  # convenção: o erro interrompe a aplicação
            vals.append(v)

        # Premissa 3: ρ0[p1↦v1, ..., pn↦vn] — NOVO dicionário a partir do
        # ambiente do CLOSURE (escopo léxico!). A notação da §3 é extensão
        # sucessiva: em nomes repetidos, o último vínculo vence.
        novo_env: Environment = {**v_f.env, **dict(zip(v_f.params, vals))}

        # Premissa 4: ⟨e_b, ρ0[...]⟩ ⇓ v — o valor da aplicação é o do corpo
        return eval(v_f.corpo, novo_env)

    # Operador unário: aplica (Op) com f_op↑, ver "Operações Aritméticas"
    if len(ast) == 2:
        op_token, expr = ast[0], ast[1]
        if not isinstance(op_token, Token) or op_token.type not in (TokenType.ADD, TokenType.SUB):
            return Erro(f"RUNTIME: operador unário inválido '{op_token}'")
        v = eval(expr, env)
        if isinstance(v, Erro):
            return v
        operador = "u+" if op_token.type == TokenType.ADD else "u-"
        # aljabr v2 (§3): v pode ser um closure — o lift devolve erro
        # ("caso contrário" do f↑), nenhuma regra nova é necessária
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
        # aljabr v2 (§3): v1/v2 podem ser closures — o lift já produz erro
        # (é o "caso contrário" do f↑; nenhuma regra nova é necessária)
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
