# Especificação de `calc`

## Sintaxe

### Conceitual, idealizada

```python
exp    ::= exp + termo | exp - termo | termo
termo  ::= termo * fator | termo / fator | fator
fator  ::= atomo ** fator | atomo
atomo  ::= INTEIRO | ( exp )
```

### EBNF efetiva usada

```python
exp     ::= termo { ( + | - ) termo }
termo   ::= fator { ( * | / ) fator }
fator   ::= atomo [ ** fator ]
atomo   ::= INTEIRO | ( exp )
```

### AST

- precedência de operadores: `**` > `*`, `/` > `+`, `-`
- os operadores `+`, `-`, `*` e `/` são associativos à esquerda
- o operador `**` é associativo à direita

Como optamos por uma gramática em EBNF e uma implementação de referência com um
parser descendente recursivo, precisamos fazer nossa gramática ser LL(1) e,
portanto, sem recursões à esquerda. Apesar disso, a linguagem exige as
associatividades acima indicadas.


## Semântica Operacional Big-Step de `calc-v2`

## Domínios Semânticos

| Domínio                                       | Descrição                                                                  |
|-----------------------------------------------|----------------------------------------------------------------------------|
| $ℝ$                                           | Os números reais.                                                          |
| $\mathrm{Val} = ℝ ∪ \\{ \mathtt{erro} \\}$    | *Os valores possíveis*: os reais ou o valor especial `erro`                |
| $\mathit{Env} = \mathit{Var} ⇀ \mathit{Val}$  | Domínio dos ambientes (estado semântico)                                   |

> **Nota:** `Var` é o conjunto (infinito) de identificadores válidos da linguagem.


## Regras de Avaliação

### Números

$$
\[
\frac{}{\langle n, \rho \rangle \Downarrow n} \quad \text{(Num)}
\]
$$

### 4.2 Operações Aritméticas

Para cada operador binário `op ∈ {+, -, *, /}`:

$$
\frac{
  \langle e_1, \rho \rangle \Downarrow v_1 \qquad
  \langle e_2, \rho \rangle \Downarrow v_2 \qquad
  f_{\mathrm{op}}(v_1,v_2) = v
}{
  \langle e_1 \text{ op } e_2, \rho \rangle \Downarrow v
} \quad \text{(Op)}
$$

### 4.3 Divisão por Zero (Erro)

$$
\[
\frac{
  \langle e_1, \rho \rangle \Downarrow v_1 \qquad
  \langle e_2, \rho \rangle \Downarrow 0
}{
  \langle e_1 \text{ / } e_2, \rho \rangle \Downarrow \mathbf{erro}
} \quad \text{(DivZero)}
\]
$$

### 4.4 Propagação de Erro

$$
\frac{
  \langle e_1, \rho \rangle \Downarrow \mathbf{erro}
}{
  \langle e_1 \text{ op } e_2, \rho \rangle \Downarrow \mathbf{erro}
} \quad \text{(ErrEsq)}
\qquad
\frac{
  \langle e_2, \rho \rangle \Downarrow \mathbf{erro}
}{
  \langle e_1 \text{ op } e_2, \rho \rangle \Downarrow \mathbf{erro}
} \quad \text{(ErrDir)}
$$
