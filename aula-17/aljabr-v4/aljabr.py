import sys
import re
import argparse
from dataclasses import dataclass
from tipos import Ast, Erro, monadic_error, Token, TokenType
from lexer import tokenizador
from parser import parser, parse_programa

def remover_comentarios(code: str) -> str:
    """Remove comentários do código-fonte.

    Todo o conteúdo de uma linha a partir do primeiro ``#`` é ignorado,
    permitindo comentários de fim de linha (inline) e de linha inteira.
    A quebra de linha de cada linha é preservada, de modo que o espaçamento
    entre linhas do código original é mantido e nenhum elemento core da
    linguagem (lexer, parser, eval) é afetado.
    """
    linhas = code.split("\n")
    resultado = []
    for linha in linhas:
        idx = linha.find("#")
        if idx != -1:
            linha = linha[:idx]
        resultado.append(linha)
    return "\n".join(resultado).strip()


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
    # aljabr v3 (§2): operadores de comparação — mesma família do (Op)
    # binário: lift f↑ cobre closures (retorna erro) e propagação de erro
    "==": lambda a, b: int(a == b),
    "<": lambda a, b: int(a < b),
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


# aljabr v4 (§3): Val = ℝ ∪ Clo ∪ Tag ∪ {erro}
# Valores etiquetados K(v1,...,vn) — dataclass imutável ao lado de Closure,
# seguindo o mesmo estilo (§4.3).
@dataclass(frozen=True)
class Tagged:
    tag: str      # K — nome do construtor
    args: tuple   # (v1, ..., vn) — valores dos componentes


# aljabr v4 (§3): Val = ℝ ∪ Clo ∪ Tag ∪ {erro}
type Val = int | float | Erro | Closure | Tagged


# aljabr v4 (§3): relação auxiliar casa(p, v) = θ ou ⊥
# Implementa (PVar), (PCuringa), (PLit), (PCons) do README.md.
# Retorna um dicionário {variavel: valor} se o padrão casa, ou None se não casa.
def casa(padrao: Ast, valor: Val) -> dict[str, Val] | None:
    # (PVar): casa(x, v) = {x -> v}
    if isinstance(padrao, str) and padrao != "_":
        return {padrao: valor}

    # (PCuringa): casa(_, v) = {}
    if padrao == "_":
        return {}

    # (PLit): casa(n, n) = {} se o valor é o mesmo inteiro
    if isinstance(padrao, int):
        if isinstance(valor, int) and padrao == valor:
            return {}
        return None

    # (PCons): casa(K(p1,...,pn), K(v1,...,vn)) = theta1 U ... U thetan
    if isinstance(padrao, list) and padrao and padrao[0] == "construtor-padrao":
        _, nome, subpadroes = padrao
        if not isinstance(valor, Tagged) or valor.tag != nome:
            return None
        if len(subpadroes) != len(valor.args):
            return None
        resultado: dict[str, Val] = {}
        for p, v in zip(subpadroes, valor.args):
            theta = casa(p, v)
            if theta is None:
                return None
            # Verificar variáveis duplicadas no padrão (já validado pelo parser,
            # mas mantido como defesa aqui)
            for var in theta:
                if var in resultado:
                    return None
            resultado.update(theta)
        return resultado

    # Qualquer outro caso: ⊥
    return None


# aljabr v4: função de apresentação (não afeta a semântica).
# Formata um valor Val para exibição legível no terminal.
# Usada apenas pelo main() quando a flag -p/--pretty-print está ativa.
def formatar_valor(v: Val) -> str:
    """Converte um valor Val em string legível para exibição.

    Valores etiquetados (Tagged) são impressos como construtores:
      Tagged('Cons', (1, Tagged('VaziaLista', ())))  ->  "Cons(1, VaziaLista)"
      Tagged('VaziaLista', ())                       ->  "VaziaLista"

    Erros e fechamentos recebem representação simplificada.
    Números são impressos normalmente.
    """
    if isinstance(v, Tagged):
        args = ", ".join(formatar_valor(a) for a in v.args)
        return f"{v.tag}({args})" if v.args else v.tag
    if isinstance(v, Erro):
        return f"Erro({v.msg})"
    if isinstance(v, Closure):
        return "<funcao>"
    return str(v)


@monadic_error
def eval(ast: Ast, env: Environment, delta: dict[str, int] | None = None) -> Val:
    # delta: conjunto de construtores declarados (nome -> aridade).
    # É opcional (default {}) para manter compatibilidade com chamadas
    # no estilo v3: eval(ast, env).
    if delta is None:
        delta = {}

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
        v1 = eval(e1, env, delta)
        if isinstance(v1, Erro):
            return v1
        new_env = {**env, var: v1}
        return eval(e2, new_env, delta)

    # Regra (LetRec) (v3, §2): ⟨letrec f = fn (p1,...,pn) ⇒ e_f in e2, ρ⟩ ⇓ v2
    # Com a primeira premissa EM EQUAÇÃO (não passo a passo): ρ1 é o ρ em
    # que f já aponta para o seu próprio closure — `novo_env[var] = Closure`
    # registra o vínculo num dicionário que o próprio closure "enxerga".
    if len(ast) == 4 and ast[0] == "letrec":
        _, var, fn_ast, body = ast
        novo_env: Environment = dict(env)
        novo_env[var] = Closure(tuple(fn_ast[1]), fn_ast[2], novo_env)
        # a segunda premissa é avaliada no ρ1 recém-construído
        return eval(body, novo_env, delta)

    # Regra (If) (v3/v4, §2): ⟨if c then e1 else e2, ρ⟩ ⇓ v
    # (IfVerd)   ⟨c,ρ⟩⇓n, n ∈ ℝ, n ≠ 0  ⇒  ⟨e1,ρ⟩⇓v
    # (IfFalso)  ⟨c,ρ⟩⇓n, n = 0         ⇒  ⟨e2,ρ⟩⇓v
    # (IfCond)   ⟨c,ρ⟩⇓v_c, v_c ∉ ℝ     ⇒  erro (condição não é número)
    #            (ajuste v4: cobre closures E valores etiquetados)
    if len(ast) == 4 and ast[0] == "if":
        cond = eval(ast[1], env)
        if isinstance(cond, Erro):
            return cond  # propagação monádica (convenção §3)
        if not isinstance(cond, (int, float)):
            return Erro("RUNTIME: condição de 'if' não é um número")
        if cond != 0:  # (IfVerd): n ≠ 0
            return eval(ast[2], env, delta)
        return eval(ast[3], env, delta)  # (IfFalso): n = 0

    # aljabr v4 (§3): construção de valor etiquetado — (Cons) / (ConsInvalido)
    # AST: ["construir", nome, args]
    if len(ast) == 3 and ast[0] == "construir":
        _, nome, args = ast

        # (ConsInvalido): construtor não declarado ou aridade errada → erro.
        # Verificação vem ANTES de avaliar os argumentos (como (AppAridade)).
        if nome not in delta:
            return Erro(
                f"RUNTIME: construtor '{nome}' não declarado"
            )
        aridade_esperada = delta[nome]
        if len(args) != aridade_esperada:
            return Erro(
                f"RUNTIME: aridade incorreta para '{nome}': "
                f"esperava {aridade_esperada} argumento(s), "
                f"recebeu {len(args)}"
            )

        # (Cons): avaliar argumentos e construir K(v1, ..., vn)
        valores: list[Val] = []
        for a in args:
            v = eval(a, env, delta)
            if isinstance(v, Erro):
                return v  # propagação de erro
            valores.append(v)
        return Tagged(nome, tuple(valores))

    # aljabr v4 (§3): expressão match — (Match) / (MatchNenhum)
    # AST: ["match", alvo, [(padrao, corpo), ...]]
    if len(ast) == 3 and ast[0] == "match":
        _, alvo, ramos = ast

        # 1ª premissa de (Match): avaliar o alvo
        v = eval(alvo, env)
        if isinstance(v, Erro):
            return v  # propagação de erro

        # Tentar ramos de cima para baixo (ordem está na regra)
        for padrao, corpo in ramos:
            theta = casa(padrao, v)
            if theta is not None:
                # (Match): primeiro ramo que casa; estende ambiente com θ
                novo_env: Environment = {**env, **theta}
                return eval(corpo, novo_env, delta)

        # (MatchNenhum): nenhum ramo casa → erro
        return Erro("RUNTIME: match sem ramo que casa com o valor")

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
        v_f = eval(e_f, env, delta)
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
            v = eval(a, env, delta)
            if isinstance(v, Erro):
                return v  # convenção: o erro interrompe a aplicação
            vals.append(v)

        # Premissa 3: ρ0[p1↦v1, ..., pn↦vn] — NOVO dicionário a partir do
        # ambiente do CLOSURE (escopo léxico!). A notação da §3 é extensão
        # sucessiva: em nomes repetidos, o último vínculo vence.
        novo_env: Environment = {**v_f.env, **dict(zip(v_f.params, vals))}

        # Premissa 4: ⟨e_b, ρ0[...]⟩ ⇓ v — o valor da aplicação é o do corpo
        return eval(v_f.corpo, novo_env, delta)

    # Operador unário: aplica (Op) com f_op↑, ver "Operações Aritméticas"
    if len(ast) == 2:
        op_token, expr = ast[0], ast[1]
        if not isinstance(op_token, Token) or op_token.type not in (TokenType.ADD, TokenType.SUB):
            return Erro(f"RUNTIME: operador unário inválido '{op_token}'")
        v = eval(expr, env, delta)
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
        v1 = eval(e1, env, delta)
        if isinstance(v1, Erro):
            return v1
        v2 = eval(e2, env, delta)
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
    parser_cli = argparse.ArgumentParser(description="Interpretador de aljabr v4")
    parser_cli.add_argument(
        "-p", "--pretty-print",
        action="store_true",
        help="imprime valores etiquetados de forma simplificada (ex.: Cons(1, Vazia))",
    )
    parser_cli.add_argument(
        "arquivo",
        nargs="?",
        help="arquivo .al com o programa (omite para ler da entrada padrão)",
    )
    args = parser_cli.parse_args()

    if args.arquivo:
        programa = open(args.arquivo).read()
    else:
        programa = sys.stdin.read()

    # limpa código
    programa = remover_comentarios(programa)
    programa = re.sub(r'\n{2,}', '\n\n', programa)

    tokens = tokenizador(programa)
    if isinstance(tokens, Erro):
        print(f"{programa}")
        print(f"-->  {tokens}")
        return

    # parse_programa retorna (ast, delta): AST e conjunto de construtores
    resultado = parse_programa(tokens)
    if isinstance(resultado, Erro):
        print(f"{programa}")
        print(f"-->  {resultado}")
        return
    ast, delta = resultado

    # O ambiente ρ inicia vazio para aljabr
    env: Environment = {}
    significado = eval(ast, env, delta)

    print(f"{programa}\n")
    if args.pretty_print:
        # Apenas apresentação: formata Tagged de forma legível
        print(f"-->  {formatar_valor(significado)}")
    else:
        print(f"-->  {significado}")


if __name__ == "__main__":
    main()
