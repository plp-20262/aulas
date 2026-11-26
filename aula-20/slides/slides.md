---
title: "Tipos Estáticos"
subtitle: "Unidade 8 / Aula 20<br>Linguagem Church com Sistema Estático de Tipos"
author: "Dalton Serey"
date: "25 de novembro de 2026"
pagetitle: "Aula 19 — Closures × objetos, encapsulamento e o problema da expressão"
lang: pt-BR
theme: white
center: false
hash: true
controls: false
progress: false
transition: none
margin: 0.03
---

## Recordemos Aljabr v3…

```text
aljabr v3 ┬──> aljabr v4 (tipos algébricos, `match`)
          └──> algora    (estado, comandos, `while`) ──> (objetos)
```

::: notes
- na Unidade 08 vamos retomar [Aljabr v3]{.highlight}
- diferente de nossa última versão, a versão [v3]{.highlight} é bem mais simples
  - não tem suporte a _Tipos Algébricos de Dados_
  - e sequer tem laços `while`
:::

. . .

```aljabr
let dobro = fn (x) => x * 2 in
dobro(21)
```

```{.aljabr include="../church-v1/exemplos/fatorial2.al"}
```

## Mas… que valores produzem estes exemplos?

```aljabr
2 + (1 < 2)
```

. . .


```aljabr
(fn (n) => n + 1) + 2
```
. . .


```aljabr
let f = 10 in
f(2)
```

. . .

```aljabr
let soma1 = fn (x) => x + 1 in
soma1(fn (y) => 2 * y)
```

## E estes dois?

```aljabr
letrec f = fn (n) =>
  if n == 0 
    then 1 
    else n + (fn (x) => x)
in
f(0)
```
. . .

```aljabr
letrec f = fn (n) =>
  if n == 0 
    then 1 
    else n + (fn (x) => x)
in
f(1)       # só mudei o valor do argumento!
```
::: notes

Neste slide mostramos o problema de não termos sistema de tipos.
:::


## O que os programas têm em comum?

Todos esses programas…

1) têm erros de programação que [não são de sintaxe]{.highlight}
2) produzem um [`erro`]{.highlight} como resultado ou…
3) … pior, produzem [dados questionáveis]{.highlight}!

. . .
  
Mais ainda… em todos os casos, o defeito [**está no texto do
programa**]{.red} e não depende de nenhum valor de entrada.

E como as diferenças entre um número e uma função ou o resultado de uma
comparação são propriedades do texto, é razoável assumir que [pode ser
verificada **sem executar**]{.red}.

## Este é nosso problema central {.concept}

Como podemos projetar uma linguagem de modo que erros dessa
natureza sejam [**detectados antes da execução**]{.red},
apenas examinando o código do programa?

. . .

::: {.destaque}
E esse é o problema que [sistemas de tipos]{.highlight} resolvem.
:::

## Mas… o que é um tipo?

Quando estudamos programação, costumamos dizer que um tipo é:

- um conjunto de valores (e suas representações)
- e o conjunto de operações que se aplica a esses valores

Esta visão, contudo, foca no [tempo de execução]{.highlight} do programa.
Nesta unidade do curso, contudo, convém focar no [**tempo de análise**]{.red}
dos programas (que às vezes chamamos de _tempo de compilação_).

. . .

Por isso, esta definição é preferível.

::: {.destaque}
Um tipo é uma abstração que caracteriza uma coleção de possíveis valores e determina como esses valores podem ser usados por um programa. Em tempo de análise, um tipo se reduz a um _nome_ que expressa um conjunto de valores possíveis.
:::

::: notes
IMPORTANTE: as duas definições se complementam! Elas não são inconsistentes. As
diferenças são consequência do foco de interesse que temos quando usamos cada
uma das duas.

:::

## Tipos e expressões

Uma consequência desta nova definição de _tipo_ é que ela nos permite
atribuir tipos não apenas a [valores]{.highlight}, mas também a [expressões]{.highlight}.

Essa mudança de foco tem um propósito: queremos poder dizer e demonstrar que
uma dada expressão `e` tem (ou não) certo tipo `T`.

. . .

::: {.destaque}
Dizer que a expressão `e` tem o tipo `T` é
[prometer]{.highlight} que, em tempo de execução,
**se** a avaliação da expressão terminar, o valor
produzido será pertencente ao tipo `T`.
:::

Afirmações como essa expressam uma propriedade esperada do programa em _tempo
de execução_.

::: notes
Observe que tipo continua sendo o conceito semântico associado a valores. Mas
agora obtém também um caráter sintático: é um nome que associo a expressões e
variáveis do programa. E os dois se relacionam porque os tipos de expressões
são expectativas ou promessas dos tipos que tais expressões vão produzir ou a
que as variáveis serão ligadas.

E, idealmente, queremos comprová-las ou refutá-las em _tempo de
análise_ (antes da execução do programa).
:::

## Analisemos o código Python abaixo

```python
x = 3
y = x / 2 + 1
```

. . . 

| Expressão ou variável  | Tipo |
|------------------------|---------------------|
| `3`                    | `int`
| `x`                    | `int`
| `2`                    | `int`
| `1`                    | `int`
| `x / 2`                | `float`
| `x / 2 + 1`            | `float`
| `1`                    | `float`

Mas como chegamos a essas conclusões?

## Sistema de tipos dinâmico

Um sistema de tipos (dinâmico) é um conjunto de regras que [classifica os
valores]{.highlight} de um programa segundo seus tipos, para [**detectar**]{.green},
[**durante a execução**]{.red}, a aplicação de operações a valores inadequados.

. . .

Um sistema de tipos dinâmico oferece dois componentes:

1. uma **notação de tipos** (e, se a linguagem permitir, anotações opcionais no
   programa)
2. um conjunto de **regras de tipo** que verificam, a cada operação, se os
   [**valores**]{.red} são coerentes com ela, e sinalizam erro quando não são

. . .

:::{.destaque}
Python tem um sistema de tipos dinâmico. De fato, Aljabr tem uma versão _light_ também, já que, em tempo de execução, indica erros quando as operações não podem ser aplicadas (graças a nosso _lift_).
:::


## Sistema de tipos (estático)

Um sistema de tipos (estático) é um conjunto de regras
que [classifica as expressões]{.highlight} de um
programa segundo os tipos de valores que elas
produzirão, para [**garantir**]{.green}, [**antes da execução**]{.red}, a
ausência de erros.

. . .

Um sistema de tipos estático oferece dois componentes:

1. uma **notação de tipos** (e, se a linguagem exigir, uma forma de fazer anotações no programa)
2. um conjunto de **regras de tipos** que atribuem tipos às [**expressões**]{.red} e que rejeitam usos considerados inválidos

:::{.destaque}
É isto que queremos especificar e implementar nesta unidade.
:::

## `Church` = Aljabr + sistema de tipos {.concept}

`church` = `aljabr` v3 + **anotações de tipo** + **verificador estático**

```text
aljabr v3 ┬──> aljabr v4 (+ tipos algébricos, `match`)
          ├──> algora    (+ estado, comandos, `while`) ──> objetos
          └──> church    (+ anotações e verificação estática)
```

. . .

- a nova LP varia **só** na dimensão *tipos*, em relação a Aljabr
- o sistema de tipos cobrirá aritmética, variáveis, funções, `letrec` e `if`
- nome em homenagem a _Alonzo Church_
  - criador do cálculo Lambda simplesmente tipado (1940)


## Um pipeline com uma etapa nova {.small style="--code-scale: 0.95"}

```text
  código fonte
      ↓
  [ lexer ]             ← REGEX
      ↓
  [ parser ]            ← EBNF
      ↓
  AST com anotações
      ↓
  [ verificador ]       ← regras de tipo       Γ ⊢ e : τ   ← NOVO
      ↓
  AST aprovada + tipo τ
      ↓
  [ interpretador ]     ← regras de avaliação  ⟨e, ρ⟩ ⇓ v
      ↓
  resultado
```

Programa rejeitado pelo verificador [**nunca executa**]{.red}.

:::notes
Observe que se trata de uma _nova ferramenta_ do processamento da linguagem
que precisa ser encaixada no _pipeline_ estabelecido.

O sistema de tipos permitirá anotar o código fonte, logo exige ajustes no
léxico e sintático. Assim, a AST passa a incluir as anotações de tipo.

O melhor ponto para a verificação é justamente entre o parser e avaliador. O
verificador percorrerá a AST contendo as anotações para provar ou refutar as
anotações de tipos que, como dissemos, podem ser vistas como _promessas_ do
programador a serem checadas.

:::

## Adição do tipo `bool` a nossa linguagem

Recordem que na Aula 14, por simplicidade, optamos por não adicionar boolean
explícito na linguagem. Decidimos usar números para decisões. Nossas opções
eram (e são) as seguintes.

| Opção da linguagem | Como tratar [`2 + (1 < 2)`]{.red}? |
|-------|---------------|
| números como condições (`0` é falso) | aceitar (vale `3`) |
| tpo `Num` distinto de `Bool` | rejeitar |

. . .

<br>Por isso, em [**Churh**]{.red} teremos:

- um novo tipo `Bool`, com literais `verdadeiro` e `falso`
- operadores `==` e `<` produzem `Bool` (e só aceitam `Num`)
- e o `if` exige condição `Bool`

::: notes
Nomes em português para não colidir com `true`/`false` da biblioteca de booleans
da Aula 12.
:::


## Onde o programador escreverá os tipos?

| Opção | Exemplo |
|-------|---------|
| anotar tudo | `let x: Num = 1 in …` |
| anotar só **onde é necessário** | `fn (x: Num) => x + 1` |
| inferir tudo (Hindley–Milner) | `fn (x) => x + 1` |

. . .

<br>Para [**Churh**]{.red} optei por:

- [parâmetros]{.highlight} sempre anotados
- [tipo de retorno do `letrec`]{.highlight} anotado
- `let` e `fn` comum: o verificador **sintetiza** o tipo de baixo para cima

. . .

<br>

Inferência (opção 3) é um algoritmo à parte: fora de escopo do curso!


## Por que o `letrec` precisa do tipo de retorno?

Se optamos por **sintetizar** o tipo de retorno de `fn`, porque não fazemos o
mesmo com funções `letrec`?

```aljabr
letrec fat = fn (n: Num) : Num =>
  if n == 0 then 1 else n * fat(n - 1)
in
fat(5)
```

O problema é que, no corpo, a chamada `fat(n - 1)` precisa de um tipo. De onde
o poderíamos obter?

. . .

O tipo de `fat` depende do tipo do corpo, que é o que estamos calculando. Há,
portanto, [**um ciclo**]{.red}. A anotação obrigatória **quebra o ciclo**.


## Como anotaremos tipos de funções?

Funções também têm tipos. O tipo combina os tipos do domínio
e do contradomínio ou, em _computês, os dos parâmetros e do valor de
retorno. Abaixo, temos duas opções de notação.

| Opção de linguagem | Função de dois números para número |
|-------|------------------------------------|
| seta entre tipos (ML, Haskell) | `Num -> Num -> Num` |
| **lista de parâmetros** e seta | `(Num, Num) -> Num` |

. . .

A primeira opção é apropriada para LPs em que as funções são _curried_. Não é
nosso caso. Logo, para [**Church**]{.red}, decidi pela segunda opção. A lista é
**sempre** _parentesada_:

- `(Num) -> Num`
- `() -> Bool`
- `(Num, Num) -> Bool`


## E o que resta para o tempo de execução?

Se a verificação é feita em tempo de análise, como o sistema de tipos deve afetar o interpretador em tempo de execução?

. . . 

| Opções para a linguagem                    | Tipos na execução?           |
|--------------------------------------------|------------------------------|
| executar e verificar dinamicamente (*)     | os valores carregam o tipo   |
| verificar antes e **apagar** os tipos      | não existem, `eval` não muda |
| verificar antes e manter tipos nos valores | existem                      |

. . .

Para [**Church**]{.red} adotei a segunda opção acima, conhecida como [apagamento de tipos]{.highlight} (*type erasure*).

::: {.destaque}
O verificador estático garante as verificações e só entrega código validado para o
avaliador. Por isso, o avaliador pode **ignorar as anotações**. Não mexemos
em nenhuma regra de avaliação.
:::

## Como são programas em [**Church**]{.red}?

```aljabr
let dobro = fn (x: Num) => x * 2 in
dobro(21)
```

. . .

```aljabr
let twice = fn (f: (Num) -> Num) => fn (x: Num) => f(f(x)) in
twice(fn (n: Num) => n + 1)(0)
```

. . .

Igual a `aljabr` v3, exceto:

1. [parâmetros]{.highlight} vêm com tipo (`x: Num`)
2. [`letrec`]{.highlight} ganha o tipo de retorno


## Exemplos que não são válidos em [**Church**]{.red}

Relembre que optamos por não termos tipos nas variáveis. Os tipos são
sintetizados das expressões.
```algora 
let x: Num = 10 in                     # erro sintático
10 < x
```

Funções lambda só têm tipos nos parâmetros, não de retorno. Mesmo motivo acima.
```algora
let f = fn (x: Num, y: Num): Num =>    # outro erro sintático
  x * y + 1
in
f(10, 20) + 1
```


## Resumo dos tipos de `church`

| Tipo | Classifica |
|------|------------|
| `Num` | números |
| `Bool` | `verdadeiro`, `falso`, resultados de comparações |
| `(τ₁, …, τₙ) -> τ` | funções de `n` argumentos |

| Tipo | Lê-se |
|------|-------|
| `(Num) -> Num` | recebe número, devolve número |
| `() -> Num` | sem argumentos, devolve número |
| `((Num) -> Num, Num) -> Num` | recebe uma função e um número |
| `(Num) -> (Num) -> Num` | recebe número, devolve **uma função** |


## O que o verificador promete

Programa **aprovado** ⇒ os erros não ocorrem na execução:

| Erro dinâmico de `aljabr` v3 | Em `church` |
|------------------------------|-------------|
| variável não vinculada | evitado: `x` não tem tipo |
| aritmética com valor que não é número | evitado por (T-Op) |
| aplicar algo que não é função | evitado *(Aula 21)* |
| número errado de argumentos | evitado *(Aula 21)* |
| `if` com condição que não é número | evitado *(Aula 21)* |

. . .

Chama-se [segurança de tipos]{.highlight} (*type soundness* ou *safety*).

::: {.footnote}
<br>
<br>
<br>
<br>
<br>
(*) Detalhe: a prova desta garantia está além do escopo deste curso.
:::


## O verificador **não** promete…

```aljabr
# … que o programa termina
letrec f = fn (n: Num) : Num =>       # f é bem tipado
  f(n)
in
f(1)
```

. . . 

```aljabr
# … que não ocorrerá `erro` em tempo de execução
1 / 0          # tem tipo Num e vale erro
```
. . . 

```aljabr
# … que o programa faz o que você quer
x + 2         # no lugar `x * 2` será aceito
```

## O verificador é conservador… 

```aljabr
if verdadeiro then 1 else 2 + verdadeiro      # será rejeitado
```

```aljabr
if 3 < 5 then verdadeiro else 2 + 3           # será rejeitado
```

Nenhuma execução chega ao `else`, mas os programas são **rejeitados**.

::: notes
Perguntar: isto é um defeito ou o preço de decidir antes de executar? Não existe
verificador que aceite exatamente os programas sem erro. Projetamos um
compromisso: rejeitar um pouco demais para nunca aceitar de menos.
:::


## Aceitos × rejeitados

| Programa | Resultado |
|----------|-----------|
| `2 + 3 * 4` | `Num` |
| `let x = 2 + 3 in x < 10` | `Bool` |
| `let x = 1 in let x = x < 2 in x` | `Bool` (sombreamento muda o tipo) |
| `2 + verdadeiro` | **erro de tipo** |
| `(1 < 2) + 1` | **erro de tipo** (era o `2 + (1 < 2)` do início!) |
| `verdadeiro == verdadeiro` | **erro de tipo** (`==` só para `Num`) |
| `x + 1` | **erro de tipo** (`x` não declarada) |
| `(let x = 1 in x) + x` | **erro de tipo** (`x` fora do escopo) |

## a ser continuado…
