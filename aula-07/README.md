# Aula 07 — 30/Set — Estágio 3 (Semana 1)

## Retomando da aula (e do Estágio) anterior

Na aula passada concluímos `calc`, nossa LP de expressões infixas com
aritmética simples. 

No diretório `calc-v2` você encontrará a implementação atualizada de `calc` de
acordo com as decisões que tomamos sobre sintaxe e sobre a produção da AST
(precedência, associatividade, aridade, etc). Em `calc-v2/README.md` documentei
isso, parcialmente.

Nosso foco, contudo, foi na _sintaxe_ da LP. Nesta aula, vamos mudar nossa
atenção para a semântica.  

> Antes de entrarmos em semântica, fizemos uma breve digressão para o
> analisador léxico. O motivo é que eu precisei reimplementar o lexer, para
> prepará-lo para as próximas etapas do curso. Leia sobre isso no arquivo
> [RENOVACAO-DO-LEXER.md](RENOVACAO-DO-LEXER.md).

## Semântica

Nas aulas anteriores, especificamos a semântica da LP por regras de transição.
Na prática, trata-se de uma _semântica operacional small-step_. O nome faz
referência ao fato de que cada regra de transição especifica como um estado
semântico durante uma computação transiciona para outro estado, ainda
intermediário. O significado, nessa abordagem, é dado pela repetição de
transições até que um estado final seja alcançado.

Nesta parte do curso, faremos a transição para regras de semântica operacional
big-step. Nesta abordagem o significado de um programa é expresso de uma única
vez, mas usando referências recursivas à relação semântica. 

## Como a formalização da semântica foi apresentada

Para as LPs anteriores, usamos regras de transição para expressar a semântica
das linguagens. Esse formalismo expressa como o estado da computação evolui de
um dado estado para outro num estilo passo-a-passo. Por isso, esse tipo de
semântica é também conhecido como _semântica operacional de pequeno passo_
(_small-step operational semantics_). Também por esse motivo, o significado do
programa (que neste caso equivale ao resultado produzido pela avaliação da
expressão) é obtido pela aplicação repetida de regras de transição até que se
obtenha uma expressão irredutível.

A partir desta aula, expressaremos a semântica formal de avaliação na forma
$⟨e, ρ⟩ ⇓ v$. Esta notação formaliza a chamada _semântica operacional de passo
grande_ (_big-step operational semantics), também chamada de _semântica
natural_ ou _semântica de avaliação_. Embora `calc-v2` seja uma LP tão simples
que possa ter sua semântica perfeitamente expressa através de regras de
transição, optei por usar semântica de avaliação como forma de  prepararmos o
caminho para nossa próxima linguagem, que inclui variáveis.

> A notação $⟨e, ρ⟩ ⇓ v$ lê-se: a expressão $e$, sob o ambiente $ρ$, avalia
> para o valor $v$. Lembre que $e$ é nosso programa e $v$ é o seu significado
> (ou seja, o resultado que queremos que seja produzido quando o programa for
> executado).

A ideia de **ambiente** (`environment`) é necessária para a introdução de
variáveis: um ambiente associa nomes a valores; avaliar uma variável, portanto,
significa consultar seu valor no ambiente corrente. Na implementação de
referência, representaremos ambientes como dicionários Python (ou lista de
dicionários, para escopos aninhados). Mais uma vez, relembre que `calc` não tem
variáveis… logo, usaremos ambientes vazios aqui.


# Semântica Operacional Big-Step de `calc-v2`

Semântica natural da LP `calc-v2`, a versão da LP que calcula expressões com
notação infixa, precedência e associatividade já implementada em sala. A
formalização segue a notação $⟨e, ρ⟩ ⇓ v$ e abre o caminho para a próxima
mini-linguagem do curso, que estenderá `calc` com **variáveis** e **ambiente**.


## 1. Sintaxe Abstrata

A sintaxe abstrata de `calc-v2` é dada pela seguinte gramática (em BNF):

```
e ::= n                      (número inteiro)
    | e1 + e2                (soma)
    | e1 - e2                (subtração)
    | e1 * e2                (multiplicação)
    | e1 / e2                (divisão inteira)
    | (e)                    (parênteses — não aparece na AST)
```

Lembrem que na AST (Abstract Syntax Tree), os parênteses não aparecem; a
estrutura da árvore já codifica a precedência e a associatividade, conforme
discutido nas aulas anteriores.


## 2. Domínios Semânticos

Um _domínio semântico_ é um conjunto matemático formal que representa algum
aspecto relativo às execuções dos programas da linguagem. Estes são os domínios
semânticos para nossa linguagem:

| Domínio                                       | Descrição                                                                  |
|-----------------------------------------------|----------------------------------------------------------------------------|
| $ℝ$                                           | Os números reais.                                                          |
| $\mathrm{Val} = ℝ ∪ \\{ \mathtt{erro} \\}$    | *Os valores possíveis*: os reais ou o valor especial `erro`                |
| $\mathit{Env} = \mathit{Var} ⇀ \mathit{Val}$  | Domínio dos ambientes (estado semântico)                                   |

O conjunto $\mathrm{Var}$ que aparece na definição do terceiro domínio
semântico acima é apenas a categoria sintática das _variáveis_ (ou
identificadores) de nossa linguagem. Para o caso específico de `calc`,
obviamente, é o conjunto vazio, já que a LP não tem variáveis. Como mencionei
em sala de aula, a ideia aqui é apenas prepararmos o caminho para nossa próxima
linguagem.

Definiremos ainda a família de funções denotadas por $f_{\mathrm{op}} = ℝ \ × \
ℝ ⇀ ℝ$. Trata-se das operações semânticas associadas aos operadores (ou
símbolos operacionais) da linguagem. Ao operador `*`, por exemplo, teremos
associada a operação $f_{*}$ que é, naturalmente, a multiplicação definida
sobre os números reais.

Por fim, observe que $\mathit{Env}$ é o domínio dos ambientes e que um
**ambiente** $ρ \in \mathit{Env}$ é uma função parcial que associa nomes de
variáveis a valores. Na próxima linguagem, $ρ$ será construído com dicionários.
Nesta versão de `calc` (em que não temos variáveis) o ambiente é sempre vazio.
A ideia, neste ponto, é que possamos introduzir a nova forma de notação formal
de semântica de forma gradual. Na próxima aula, faremos melhor uso de
ambientes. 


## 3. Forma do Julgamento

A semântica é expressa por meio de um **julgamento de avaliação**:

$$
\[
\langle e, \rho \rangle \Downarrow v
\]
$$

Lê-se: *"a expressão `e`, sob o ambiente `ρ`, avalia para o valor `v`"*.

Este julgamento é definido **indutivamente** por um conjunto de **regras de
inferência** (regras de avaliação), cada uma com a forma:
 
$$
\[
\frac{\text{premissas}}{\text{conclusão}}
\]
$$

Se todas as premissas são deriváveis, a conclusão também é. A semântica
big-step caracteriza-se por **avaliar a expressão inteira em um único passo**,
produzindo diretamente o valor final.



## 4. Regras de Avaliação

### 4.1 Números

$$
\[
\frac{}{\langle n, \rho \rangle \Downarrow n} \quad \text{(Num)}
\]
$$

Um literal numérico avalia para si mesmo, independentemente do ambiente.


### 4.2 Operações Aritméticas

Para cada operador binário `op ∈ {+, -, *, /}`:

$$
\[
\frac{
  \langle e_1, \rho \rangle \Downarrow v_1 \qquad
  \langle e_2, \rho \rangle \Downarrow v_2 \qquad
  f_{\mathrm{op}}(v_1,v_2) = v
}{
  \langle e_1 \text{ op } e_2, \rho \rangle \Downarrow v
} \quad \text{(Op)}
\]
$$

**Leitura:** para avaliar uma expressão `e1 op e2`, avaliamos primeiro `e1` no
ambiente `ρ`, obtendo `v1`; em seguida avaliamos `e2` no mesmo ambiente `ρ`,
obtendo `v2`; por fim, aplicamos a operação semântica correspondente a `v1` e
`v2`, produzindo `v`.

Note que **o ambiente não muda durante a avaliação** nesta versão: `calc-v2` é
uma linguagem puramente expressiva, sem atribuições ou vinculações. Note ainda
que a especificação formal dá uma visão recursiva para a interpretação (por
isso chamada de natural).


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

A divisão por zero é um caso especial que produz o valor `erro`, propagando-se
pela avaliação.


### 4.4 Propagação de Erro

Se uma subexpressão avalia para `erro`, o resultado da expressão inteira também
é `erro`:

$$
\[
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
\]
$$

Note o quanto essa especificação se assemelha ao esquema de erros monádico que
montamos para nossa implementação.


## 5. Exemplos de Derivação

### Exemplo 1: `2 + 3 * 4`

A AST correspondente é:

```
    +
   / \
  2   *
     / \
    3   4
```

**Derivação:**

1. `⟨2, ρ⟩ ⇓ 2` (Num)
2. `⟨3, ρ⟩ ⇓ 3` (Num)
3. `⟨4, ρ⟩ ⇓ 4` (Num)
4. `⟨3 * 4, ρ⟩ ⇓ 12` (Op, 2–3)
5. `⟨2 + (3 * 4), ρ⟩ ⇓ 14` (Op, 1 e 4)

**Conclusão:** `⟨2 + 3 * 4, ρ⟩ ⇓ 14`.

### Exemplo 2: `(2 + 3) * 4`

A AST correspondente é:

```
    *
   / \
  +   4
 / \
2   3
```

**Derivação:**

1. `⟨2, ρ⟩ ⇓ 2` (Num)
2. `⟨3, ρ⟩ ⇓ 3` (Num)
3. `⟨2 + 3, ρ⟩ ⇓ 5` (Op, 1–2)
4. `⟨4, ρ⟩ ⇓ 4` (Num)
5. `⟨(2 + 3) * 4, ρ⟩ ⇓ 20` (Op, 3–4)

**Conclusão:** `⟨(2 + 3) * 4, ρ⟩ ⇓ 20`.

Observe como é a estrutura da AST, e não a ordem textual, que determina a ordem
de avaliação.

### Exemplo 3: `10 / (5 - 5)`

1. `⟨10, ρ⟩ ⇓ 10` (Num)
2. `⟨5, ρ⟩ ⇓ 5` (Num)
3. `⟨5, ρ⟩ ⇓ 5` (Num)
4. `⟨5 - 5, ρ⟩ ⇓ 0` (Op, 2–3)
5. `⟨10 / (5 - 5), ρ⟩ ⇓ erro` (DivZero, 1 e 4)

**Conclusão:** `⟨10 / (5 - 5), ρ⟩ ⇓ erro`.


## 6. Propriedades da Semântica Big-Step

- **Determinismo:** para toda expressão `e` e todo ambiente `ρ`, se `⟨e, ρ⟩ ⇓
v₁` e `⟨e, ρ⟩ ⇓ v₂`, então `v₁ = v₂`. Isto é, a semântica é uma **função
parcial** de expressões para valores.

- **Composicionalidade:** o valor de uma expressão é determinado exclusivamente
pelos valores de suas subexpressões imediatas. Isso se reflete diretamente na
estrutura das regras de inferência.

- **Independência do ambiente:** em `calc-v2` (sem variáveis), o ambiente `ρ` é
irrelevante: o valor de qualquer expressão independe de `ρ`. Na próxima
linguagem, isso deixará de ser verdade.


## 7. Alternativas

Discutimos no final da aula que haveria alternativas à forma como expressamos
as regras acima. Por exemplo, se a família de funções ou operações que usamos
for de funções totais (ou seja, se pudermos garantir que elas produzem um valor
válido para todo valor do domínio), poderíamos simplificar o conjunto de regras
de inferência. Por exemplo, a regra $\text{Op}$ que definimos acima, estabele
como premissa a existência de um valor $v$ que seja o resultado de
$f_{\mathrm{op}}(v_1,v_2)$. Isso permite usar essa regra mesmo que a operação
$f_{\mathrm{op}}$ não esteja definida para certos valores. Quando isso ocorre,
a premissa não existe e, portanto, a regra não se pode aplicar. Isso nos obriga
a aplicar outra regra ou, se isso não for possível, se configurará uma situação
de bloqueio da execução (_stuck state_).

Uma alternativa seria garantir que as operações sejam totais. Uma forma simples de fazer
isso é aplicar um _lift_ às operações parciais originais.
O _lift_ produz funções equivalentes às originais nos valores em que estão definidas, mas produzem

o valor $\mathrm{erro}$ para os valores do domínio em que não está definida. O
_lift_ quando aplicado a funções do tipo $f : \mathbb{R} \times \mathbb{R}
\rightharpoonup \mathbb{R}$ produz funções do tipo $f : \mathrm{Val} \times
\mathrm{Val} \rightharpoonup \mathrm{Val}$. Para isso, definimos $f' =
\mathrm{lift}(f)$ como:

$$
f'(v_1, v_2) = 
\begin{cases} 
f(v_1, v_2) & \text{se } v_1, v_2 \in \mathbb{R} \text{ e } (v_1, v_2) \in \mathrm{dom}(f) \\
\mathtt{erro} & \text{em caso contrário}
\end{cases}
$$

Com essa mudança, podemos usar uma regra que assume que sempre há um valor para
$f_{\mathrm{op}}(v_1, v_2)$ e podemos colocar essa expressão diretamente na
conclusão da regra. Compare a regra abaixo com a original de $\mathrm{Op}$ dada
acima. E isso poderia dispensar as regras de inferência que produzem o erro pra
divisão por zero, porque a própria operação semântica produz $\mathrm{erro}$,
sem a necessidade de uma regra apenas para isso.

$$
\[
\frac{
  \langle e_1, \rho \rangle \Downarrow v_1 \qquad
  \langle e_2, \rho \rangle \Downarrow v_2
}{
  \langle e_1 \text{ op } e_2, \rho \rangle \Downarrow f_{\mathrm{op}}(v_1, v_2)
} \quad \text{(Op)}
\]
$$

O importante a observar aqui é que a escolha das regras de inferência e das
operações semântica é parte do projeto da linguagem.
