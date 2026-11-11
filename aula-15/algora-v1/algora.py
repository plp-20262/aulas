import sys
from dataclasses import dataclass
from lexer import tokenizador
from parser import parser
from tipos import (
    Ast, Erro, monadic_error, Token, TokenType,
    Stmt, Expr, VarDecl, Assign, FunDecl, ExprStmt, Num, Var,
    AnonFun, Call, BinaryOp, UnaryOp, IfExpr, Block
)

# ---------------------------------------------------------------------------
# Modelo de memória — dois níveis (conforme a especificação formal):
#   ρ (Environment): nome -> Loc        (mapa `env`)
#   σ (Store):        Loc -> valor      (mapa `store`)
#
# Na implementação, usamos dois dicionários planos:
#   env:   dict[str, int]  -> vínculos (variável -> endereço de memória)
#   store: dict[int, Val] -> memória (endereço -> valor)
# O store é sempre passado por parâmetro (nunca estado global).
#
# IMPORTANTE: o `env` é mutado no lugar pelos comandos (var/def) de um bloco.
# Por isso, toda closure guarda uma CÓPIA do `env` (ρ₀ no momento da criação),
# e não uma referência a ele. Assim, declarações posteriores no mesmo bloco
# (var repetido, def posterior) não alteram o ambiente capturado.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Closure:
    params: list[str]
    body: Block
    env: dict   # ρ₀ capturado (cópia)

Val = int | float | Closure | Erro

def eval_stmt(stmt: Stmt, env: dict[str, int], store: dict[int, Val]) -> Erro | None:
    match stmt:
        case VarDecl(name, init_expr):
            # o inicializador é avaliado ANTES de `name` entrar no ambiente
            v = eval_expr(init_expr, env, store)
            if isinstance(v, Erro):
                return v
            loc = max(store, default=0) + 1
            env[name] = loc
            store[loc] = v
            return None

        case Assign(name, value_expr):
            if name not in env:
                return Erro(f"RUNTIME: variável '{name}' não declarada")
            v = eval_expr(value_expr, env, store)
            if isinstance(v, Erro):
                return v
            store[env[name]] = v
            return None

        case FunDecl(name, params, body):
            loc = max(store, default=0) + 1
            env[name] = loc
            # a cópia é feita DEPOIS de ligar `name`: a recursão direta funciona,
            # mas nada declarado posteriormente fica visível (sem "hoisting")
            store[loc] = Closure(params, body, dict(env))
            return None

        case ExprStmt(expr):
            v = eval_expr(expr, env, store)
            if isinstance(v, Erro):
                return v
            return None

def eval_pow(v1: int | float, v2: int | float) -> Val:
    # ** é parcial sobre ℝ: nunca deve vazar exceção do Python nem número complexo
    try:
        r = v1 ** v2
    except ZeroDivisionError:
        return Erro("RUNTIME: divisão por zero")
    except OverflowError:
        return Erro("RUNTIME: resultado fora do domínio")
    if isinstance(r, complex):
        return Erro("RUNTIME: resultado não real")
    return r

@monadic_error
def eval_expr(expr: Expr, env: dict[str, int], store: dict[int, Val]) -> Val:
    match expr:
        case Num(val):
            return val

        case Var(name):
            if name not in env:
                return Erro(f"RUNTIME: variável '{name}' não vinculada")
            return store[env[name]]

        case AnonFun(params, body):
            return Closure(params, body, dict(env))

        case Call(callee, args):
            v_f = eval_expr(callee, env, store)
            if isinstance(v_f, Erro):
                return v_f
            if not isinstance(v_f, Closure):
                return Erro("RUNTIME: aplicação de não-função")
            if len(args) != len(v_f.params):
                return Erro(
                    f"RUNTIME: aridade incorreta: esperava {len(v_f.params)} "
                    f"argumento(s), recebeu {len(args)}"
                )
            vals = []
            for a in args:
                v = eval_expr(a, env, store)
                if isinstance(v, Erro):
                    return v
                vals.append(v)
            call_env = dict(v_f.env)
            for param, val in zip(v_f.params, vals):
                loc = max(store, default=0) + 1
                call_env[param] = loc
                store[loc] = val
            return eval_expr(v_f.body, call_env, store)

        case BinaryOp(op, left, right):
            v1 = eval_expr(left, env, store)
            if isinstance(v1, Erro):
                return v1
            v2 = eval_expr(right, env, store)
            if isinstance(v2, Erro):
                return v2
            if not isinstance(v1, (int, float)) or not isinstance(v2, (int, float)):
                return Erro("RUNTIME: operação sobre valor não-numérico")
            match op:
                case "+": return v1 + v2
                case "-": return v1 - v2
                case "*": return v1 * v2
                case "/": return Erro("RUNTIME: divisão por zero") if v2 == 0 else v1 / v2
                case "**": return eval_pow(v1, v2)
                case "==": return int(v1 == v2)
                case "<": return int(v1 < v2)
                case _: return Erro(f"RUNTIME: operador desconhecido '{op}'")

        case UnaryOp(op, operand):
            v = eval_expr(operand, env, store)
            if isinstance(v, Erro):
                return v
            if not isinstance(v, (int, float)):
                return Erro("RUNTIME: operação unária sobre valor não-numérico")
            return v if op == "+" else -v

        case IfExpr(cond, then_b, else_b):
            v_c = eval_expr(cond, env, store)
            if isinstance(v_c, Erro):
                return v_c
            if isinstance(v_c, Closure):
                return Erro("RUNTIME: condição do 'if' é uma função")
            if v_c != 0:
                return eval_expr(then_b, env, store)
            return eval_expr(else_b, env, store)

        case Block(stmts, final_expr):
            block_env = dict(env)
            for stmt in stmts:
                err = eval_stmt(stmt, block_env, store)
                if isinstance(err, Erro):
                    return err
            return eval_expr(final_expr, block_env, store)

@monadic_error
def executar_programa(programa: str, env: dict[str, int], store: dict[int, Val]) -> Val:
    tokens = tokenizador(programa)
    ast = parser(tokens)
    return eval_expr(ast, env, store)

def main():
    if len(sys.argv) > 1:
        programa = open(sys.argv[1]).read()
    else:
        programa = sys.stdin.read()
    resultado = executar_programa(programa, {}, {})
    print(f"Programa:\n{programa}\n")
    print(f"--> {resultado}")

if __name__ == "__main__":
    main()
