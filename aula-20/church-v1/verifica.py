"""Verificador estático de tipos de `church` v1.

Espelha `church.py` (que define `eval`): cada regra de tipo
Γ ⊢ e : τ vira uma cláusula de `verifica`, no mesmo estilo em que cada
regra de avaliação ⟨e, ρ⟩ ⇓ v vira uma cláusula de `eval`. A diferença é
o domínio: aqui calculamos TIPOS (uma abstração dos valores), não valores.

    verifica(e, gamma) -> Tipo | Erro

onde gamma é o contexto Γ: Var ⇀ Ty. O erro de tipo é a AUSÊNCIA de
derivação: quando nenhuma regra se aplica, devolvemos um `Erro`.

Fragmento da Aula 20: (T-Num), (T-Verd), (T-Falso), (T-Var), (T-Let),
(T-Op) e (T-OpUn). Aula 21: (T-Lam), (T-App), (T-If) e (T-LetRec).
"""

from tipos import Ast, Erro, Token, TokenType, monadic_error
from tipos import TNum, TBool, TFun, Tipo

# Contexto de tipos Γ: Var ⇀ Ty  (nomes → tipos).
# É para tipos o que o ambiente ρ é para valores.
type Context = dict[str, Tipo]

# church v1 (§4.5): assinaturas dos operadores — sig(op).
#
# Operadores binários: sig(op) = (τ₁, τ₂) -> τ.
SIG_BIN = {
    "+":  (TNum(), TNum(), TNum()),
    "-":  (TNum(), TNum(), TNum()),
    "*":  (TNum(), TNum(), TNum()),
    "/":  (TNum(), TNum(), TNum()),
    "**": (TNum(), TNum(), TNum()),
    "==": (TNum(), TNum(), TBool()),
    "<":  (TNum(), TNum(), TBool()),
}

# Operadores unários: sig(op) = τ₁ -> τ.
SIG_UN = {
    "+": (TNum(), TNum()),
    "-": (TNum(), TNum()),
}


@monadic_error
def verifica(e: Ast, gamma: Context) -> Tipo | Erro:
    """Γ ⊢ e : τ — uma cláusula por regra de tipo (§4.5 e Aula 21)."""
    # (T-Num)
    if isinstance(e, int):
        return TNum()

    # (T-Var): Γ(x) = τ. Se x ∉ dom(Γ), não há regra aplicável → erro.
    if isinstance(e, str):
        if e in gamma:
            return gamma[e]
        return Erro(f"variável '{e}' não declarada")

    # AST malformada
    if not isinstance(e, list):
        return Erro(f"forma de AST inválida '{e}'")

    # (T-Verd) / (T-Falso)
    if len(e) == 2 and e[0] == "bool":
        return TBool()

    # (T-Let): Γ ⊢ e₁ : τ₁  e  Γ[x ↦ τ₁] ⊢ e₂ : τ₂.
    if len(e) == 4 and e[0] == "let":
        _, x, e1, e2 = e
        t1 = verifica(e1, gamma)
        if isinstance(t1, Erro):
            return t1
        return verifica(e2, {**gamma, x: t1})

    # (T-LetRec) — Aula 21. Quebra o ciclo da recursão usando a anotação
    # de retorno: o tipo de `f` é (τ₁,…,τₙ) -> τ_ret.
    if len(e) == 5 and e[0] == "letrec":
        _, f, fn_ast, tau_ret, corpo = e
        params = fn_ast[1]                 # [(nome, tipo), ...]
        corpo_fn = fn_ast[2]
        taus = tuple(t for _, t in params)
        ftipo = TFun(taus, tau_ret)
        gamma1 = {**gamma, f: ftipo}
        # o corpo do fn deve ter o tipo de retorno anotado
        t_corpo = verifica(corpo_fn, {**gamma1, **dict(params)})
        if isinstance(t_corpo, Erro):
            return t_corpo
        if t_corpo != tau_ret:
            return Erro(
                f"corpo de '{f}' tem tipo {t_corpo}, mas o tipo de retorno "
                f"anotado é {tau_ret}"
            )
        return verifica(corpo, gamma1)

    # (T-If) — Aula 21. Condição Bool; os dois ramos com o mesmo tipo.
    if len(e) == 4 and e[0] == "if":
        _, c, e1, e2 = e
        tc = verifica(c, gamma)
        if isinstance(tc, Erro):
            return tc
        if tc != TBool():
            return Erro(f"condição de 'if' tem tipo {tc}, mas esperava {TBool()}")
        t1 = verifica(e1, gamma)
        if isinstance(t1, Erro):
            return t1
        t2 = verifica(e2, gamma)
        if isinstance(t2, Erro):
            return t2
        if t1 != t2:
            return Erro(f"ramos de 'if' têm tipos diferentes: {t1} e {t2}")
        return t1

    # (T-Lam) — Aula 21. Γ[xᵢ ↦ τᵢ] ⊢ corpo : τ  ⇒  Γ ⊢ fn(...) : (τ₁,…,τₙ) -> τ.
    if len(e) == 3 and e[0] == "fn":
        _, params, corpo = e
        taus = tuple(t for _, t in params)
        t_corpo = verifica(corpo, {**gamma, **dict(params)})
        if isinstance(t_corpo, Erro):
            return t_corpo
        return TFun(taus, t_corpo)

    # (T-App) — Aula 21. Confere que e_f é função, a aridade e os argumentos.
    if len(e) == 3 and e[0] == "app":
        _, e_f, args = e
        tf = verifica(e_f, gamma)
        if isinstance(tf, Erro):
            return tf
        if not isinstance(tf, TFun):
            return Erro(f"aplicação de não-função: tipo {tf}")
        if len(args) != len(tf.params):
            return Erro(
                f"aridade incorreta: esperava {len(tf.params)} argumento(s), "
                f"recebeu {len(args)}"
            )
        for i, a in enumerate(args):
            ta = verifica(a, gamma)
            if isinstance(ta, Erro):
                return ta
            if ta != tf.params[i]:
                return Erro(
                    f"argumento {i + 1} tem tipo {ta}, mas esperava {tf.params[i]}"
                )
        return tf.ret

    # (T-Op) binário: sig(op) = (τ₁, τ₂) -> τ; os operandos devem casar.
    if len(e) == 3:
        op_token, e1, e2 = e[0], e[1], e[2]
        if not isinstance(op_token, Token):
            return Erro(f"operador inválido '{op_token}'")
        if op_token.lexema not in SIG_BIN:
            return Erro(f"operador desconhecido '{op_token.lexema}'")
        t1 = verifica(e1, gamma)
        if isinstance(t1, Erro):
            return t1
        t2 = verifica(e2, gamma)
        if isinstance(t2, Erro):
            return t2
        tau1, tau2, tau_ret = SIG_BIN[op_token.lexema]
        if (t1, t2) != (tau1, tau2):
            return Erro(
                f"operador '{op_token.lexema}' espera ({tau1}, {tau2}), "
                f"mas recebeu ({t1}, {t2})"
            )
        return tau_ret

    # (T-OpUn): sig(op) = τ₁ -> τ; o operando deve casar.
    if len(e) == 2:
        op_token, e1 = e[0], e[1]
        if not isinstance(op_token, Token) or op_token.type not in (TokenType.ADD, TokenType.SUB):
            return Erro(f"operador unário inválido '{op_token}'")
        tau1, tau_ret = SIG_UN[op_token.lexema]
        t1 = verifica(e1, gamma)
        if isinstance(t1, Erro):
            return t1
        if t1 != tau1:
            return Erro(
                f"operador '{op_token.lexema}' espera {tau1}, mas recebeu {t1}"
            )
        return tau_ret

    return Erro(f"forma de AST inválida '{e}'")
