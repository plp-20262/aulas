# Especificação de `aljabr`

Principais mudanças na especificação da LP `aljabr` em comparação a `calc`:

- inclui categoria léxica para variáveis (categoria `NOME`)
- inclui a sintaxe para vinculações: `let..in`

## Léxico

A linguagem inclui variáveis que, no léxico, serão chamadas de `NOME`s (tal
como é feito em Python). Um nome é simplesmente um identificador formado por
letras minúsculas, dígitos e `_` (sublinha), nunca iniciados por dígito.

NOME REGEX: `r'^[a-z_][a-z0-9_]*$'`

Também precisaremos adicionar duas palavras-reservadas: `let` e `in`. O Lexer
terá tokens apropriados para cada uma das palavras reservadas.

> A estratégia no LEXER será adicionar a categoria sintática `NOME` com a
> especificação acima. Além disso, manter um mapa de palavras reservadas.
> Depois do match de um `NOME`, podemos checar se se trata de uma palavra
> reservada e retornamos o token apropriado.

## Sintaxe

### Conceitual, idealizada

```python
exp ::= INTEIRO                    (número inteiro)
      | NOME                       (identificador/variável)     ← NOVA SINTAXE
      | let NOME = exp1 in exp2    (vinculação local)           ← NOVA SINTAXE
      | exp1 + exp2                (soma)
      | exp1 - exp2                (subtração)
      | exp1 * exp2                (multiplicação)
      | exp1 / exp2                (divisão inteira)
      | exp1 ** exp2               (exponenciação)
      | + exp1                     (+ unário)
      | - exp1                     (- unário)
      | (exp)                      (parênteses)
```

### EBNF efetiva usada

```python
exp   ::= let NOME = exp in exp | termo { ( + | - ) termo }
termo ::= fator { ( * | / ) fator }
fator ::= unario [ ** fator ]
unario::= [ + | - ] atomo
atomo ::= INTEIRO | NOME | ( exp )            
```

## Semântica Operacional Big-Step de `aljabr-v1`

### Domínios Semânticos

| Domínio                                       | Descrição                                                                  |
|-----------------------------------------------|----------------------------------------------------------------------------|
| $ℝ$                                           | Os números reais.                                                          |
| $\mathrm{Val} = ℝ ∪ \\{ \mathtt{erro} \\}$    | *Os valores possíveis*: os reais ou o valor especial `erro`                |
| $\mathit{Env} = \mathit{Var} ⇀ \mathit{Val}$  | Domínio dos ambientes (estado semântico)                                   |

> **Nota:** `Var` é o conjunto (infinito) de identificadores válidos da linguagem.

### Operações Semânticas e Operadores

Para simplificar as regras de inferência, usarei apenas operações semânticas
totais, obtidas através de um _lift_. Ou seja, as operações retornarão
$\mathrm{erro}$ para todo valor do domínio em que a original está indefinida.
As funções lifted também devem propagar erros em estilo monádico. Esta decisão
permite eliminar as regras de inferência para lidar com erros de funções
parciais e as regras de propação de erro.

**Notação** Nos referiremos às operações semânticas com a notação
$f_{\text{op}}$ (original) e $f_{\text{op}}^{\uparrow}$ (_lifted_), para à
operação relacionada ao operador $\text{op}$. Por exemplo, para a operação de
soma podemos usar $f_{+}$ (original) e $f_{+}^{\uparrow}$ (_lifted_).

Se assumirmos que cada operação semântica original é uma função parcial

$$
f_{\mathrm{op}} : \mathbb{R} \times \mathbb{R} \rightharpoonup \mathbb{R},
$$

podemos definir sua versão _lifted_ como uma função total

$$
f_{\mathrm{op}}^{\uparrow} :
\mathrm{Val} \times \mathrm{Val}
\to
\mathrm{Val},
$$

em que $\mathrm{Val} = \mathbb{R} \cup \\{ \mathbf{erro} \\}$. A função _lifted_
propaga $\mathbf{erro}$ e transforma em $\mathbf{erro}$ qualquer aplicação da
operação original para a qual ela não esteja definida:

$$
f_{\mathrm{op}}^{\uparrow}(v_1,v_2) =
\begin{cases}
\mathbf{erro},
  & \text{se } v_1 = \mathbf{erro}\ \text{ou}\ v_2 = \mathbf{erro}, \\
f_{\mathrm{op}}(v_1,v_2),
  & \text{se } v_1,v_2 \in ℝ\ \text{e} \ f_{\mathrm{op}}(v_1,v_2)\mathrel{\downarrow}, \\
\mathbf{erro},
  & \text{caso contrário}.
\end{cases}
$$

Aqui, $f_{\mathrm{op}}(v_1,v_2)\mathrel{\downarrow}$ significa que a função
parcial $f_{\mathrm{op}}$ está definida para o par $(v_1,v_2)$ (notação
convencional de lógica matemática, computabilidade e funções parciais).


### Regras de Avaliação

#### Números

$$
\frac{}{\langle n, \rho \rangle \Downarrow n} \quad \text{(Num)}
$$


#### Operações Aritméticas

Para cada operador binário `Op ∈ {+, -, *, /, **}`:

$$
\frac{
  \langle e_1, \rho \rangle \Downarrow v_1 \qquad
  \langle e_2, \rho \rangle \Downarrow v_2 \qquad
  f_{\mathrm{Op}}^{\uparrow}(v_1,v_2) = v
}{
  \langle e_1 \text{ Op } e_2, \rho \rangle \Downarrow v
} \quad \text{(Op)}
$$


#### Variável

$$
\frac{\rho(x) = v}{\langle x, \rho \rangle \Downarrow v} \quad \text{(Var)}
$$

Se o ambiente associa `x` a `v`, então `x` avalia para `v`.


#### Variável Não Vinculada (Erro)

$$
\frac{x \notin \mathrm{dom}(\rho)}{\langle x, \rho \rangle \Downarrow \mathbf{erro}} \quad \text{(VarNaoLigada)}
$$

Se `x` não está no domínio de `ρ`, a avaliação resulta em `erro`. Isso
generaliza o tratamento de erro já presente em `aljabr`.

> **Importante** Se optarmos por usar a versão _lifted_ de $ρ$, esta regra é
> desnecessária, já que o valor de $ρ(x)$ é $\mathrm{erro}$ quando $x$ não
> estiver no domínio de $ρ$.

#### Vinculação Local (`let`)

$$
\frac{
  \langle e_1, \rho \rangle \Downarrow v_1 \qquad
  \langle e_2, \rho[x \mapsto v_1] \rangle \Downarrow v_2
}{
  \langle \text{let } x = e_1 \text{ in } e_2, \rho \rangle \Downarrow v_2
} \quad \text{(Let)}
$$

Ou seja, para avaliar `let x = e1 in e2`:

1. avaliamos `e1` no ambiente **corrente** `ρ`, obtendo `v1`;
2. avaliamos `e2` no ambiente **estendido** `ρ[x ↦ v1]`, obtendo `v2`;
3. o resultado é `v2`.

Observe que:

- o ambiente `ρ` **não é modificado**: `ρ[x ↦ v1]` é uma nova função;
- `e1` é avaliada **antes** de `x` ser vinculada, portanto `x` **não** está em
escopo dentro de `e1` (o `let` **não é recursivo**);
- o escopo de `x` é **estritamente** o corpo `e2`.

