## Aula 11 — 19/Out — Unidade 4: Funções e closures (parte 2/4)

> Tema da aula: início da especificação formal de `aljabr` v2 (que difere de
> `v1` pela introdução de lambdas e closures).


## Objetivo geral

Na Aula 09 decidimos _como escrever_ funções em `aljabr` e vimos,
informalmente, _o que elas devem significar_: um lambda avalia para um
**closure**, que é uma tripla `(parâmetros, corpo, ambiente de criação)`.

Nesta (e na próxima) aula transformaremos essas decisões em especificações
precisas, nos três níveis a que você já deve estar acostumado: **léxico**
(REGEX), **sintático** (EBNF) e **semântica** (regras de avaliação `⟨e, ρ⟩ ⇓
v`). Também veremos como cada especificação orienta a implementação do estágio
correspondente do pipeline.

> IMPORTANTE: a parte semântica, e a orientação para a implementação de
> referência de `aljabr` v2 só serão apresentadas na Aula 12. Até lá, como
> orientei em sala de aula, peço que você tente implementar a linguagem você
> mesmo, a partir das especificações desta aula e também das que já adiantei no
> README.md da próxima aula (Aula 12). É assim que se aprende a ler
> especificações. Faça também os exercícios que adicionei.


## Bloco 1: Retomada e o que muda no pipeline

### 1.1 Retomando a Aula 09

- Reforço que o `let` nos permite abstrair **valores** já calculados, mas
  não nos permite abstrair **computações**: precisamos de funções.

- Na Aula 09, optamos pelo seguinte design:
  > #### Decisão da turma
  > - Opção A da tabela de opções apresentada: `fn (x, y) => exp`
  > - Trata-se de um lambda com múltiplos parâmetros, sem currying.
  > #### Justificativa
  > - ancoragem léxica em `fn`;
  > - boa familiaridade e legibilidade;
  > - acomoda facilmente anotações de tipos em versões futuras;
  > - deixa `[` e `]` livres para listas.
  > #### Mas… restou uma dívida técnica sobre sintaxe
  > - a aplicação direta de um lambda precisará de parênteses:
  > - `(fn (x) => x)(1)`
  > #### Semântica
  > - valores de lambdas são **closures**: `(parâmetros, corpo, ambiente de criação)`
  > - decidimos usar o ambiente de criação (`ρ₀`), estendido com os argumentos; não o ambiente de chamada.
  > - esta opção semântica é conhecida por _escopo léxico_.

### 1.2 Rápido teste

**Qual o resultado do programa abaixo, `10` ou `103`?**

```text
let n = 7 in
let soma_n = fn (x) => x + n in
let n = 100 in
soma_n(3) + n
```
A resposta é `110`. Nesta aula, veremos como _provar_ isso, com regras (ou como _executar_ o programa, já que temos visto que provas e execuções de programas têm bastante em comum).

### 1.3 O que precisa mudar em cada estágio?

Relembre o pipeline de processamento de uma LP (que vimos inicialmente na Aula 02).
Agora associado às meta-linguagens e notações que usamos para especificar
cada estágio:

```text
  código fonte
       ↓
   [ lexer ]            ← especificado por REGEX
       ↓
    tokens
       ↓
  [ parser ]            ← especificado por EBNF
       ↓
      AST
       ↓
[ interpretador ]       ← especificado por regras de avaliação ⟨e, ρ⟩ ⇓ v
       ↓
   resultado
```

> **Pergunta:** para aceitar expressões do tipo `let quad = fn (x) => x * x in quad(3)`,
> o que precisamos mudar em cada estágio do nosso pipeline de `aljabr` versão `v1`?

| Estágio       | O que muda em `aljabr` na versão `v2`                               |
|---------------|---------------------------------------------------------------------|
| Léxico        | três novos tokens: `fn`, `=>` e `,`                                 |
| Sintaxe       | duas novas formas de expressão: lambdas e aplicações                |
| Semântica     | um novo tipo de valor (closure) e regras para criá-los e aplicá-los |


## Bloco 2: Léxico

### 2.1 Novos tokens

Apenas três novas categorias léxicas:

```text
FN     ::=  fn          (palavra reservada, como let e in)
ARROW  ::=  =>
COMMA  ::=  ,
```

O léxico completo de `aljabr` v2 fica assim:

```text
INTEIRO  ::=  [0-9]+
NOME     ::=  [a-z_][a-z0-9_]*       (exceto as palavras reservadas)
LET      ::=  let
IN       ::=  in
FN       ::=  fn                     ← NOVO
POW      ::=  \*\*
ADD      ::=  \+
SUB      ::=  -
MULT     ::=  \*
DIV      ::=  /
EQUAL    ::=  =
ARROW    ::=  =>                     ← NOVO
COMMA    ::=  ,                      ← NOVO
LPAREN   ::=  \(
RPAREN   ::=  \)
```

**Palavras reservadas.** Agora são três: `let`, `in` e `fn`. Nenhuma delas
pode ser usada como nome de variável. Observe que `fna`, `inx` ou `let1` continuam
sendo `NOME`s válidos: a reserva vale para o lexema inteiro, não para prefixos.

### 2.2 A ordem das regras importa (de novo)

Lembre do que discutimos sobre `**` e `*`: quando dois tokens compartilham um
prefixo, o mais longo deve ser tentado antes. Precisamos, portanto, usar a mesma 
lógica para evitar problemas com `=>` e `=`.

> **Pergunta:** reflita sobre o que aconteceria com `x => x` se a regra de `EQUAL`
> aparecer antes da regra de `ARROW` na lista de regras do lexer?
>
> Resposta: o lexer reconhecerá `=` como `EQUAL` e, em seguida, encontrará um `>`
> que não casará com nenhuma regra. Resuktado: erro léxico, num programa que
> deveria ser válido.

> IMPORTANTE: ainda precisamos confirmar que a ordem das categorias sintáticas
> que usei acima é a correta para a formação do REGEX único de nosso lexer (eu
> pensava que as tinha colocado na ordem certa, mas não estou mais certo; só
> implementando veremos). Tente verificar isso você mesmo. Farei isso antes da
> próxima aula.

### 2.3 Exemplo de tokenização

O programa
```
let f = fn (x) => x in
f(1)
```
será tokenizado como:

| Lexema | Categoria  |
|--------|------------|
| `let`  | `LET`      |
| `f`    | `NOME`     |
| `=`    | `EQUAL`    |
| `fn`   | `FN`       |
| `(`    | `LPAREN`   |
| `x`    | `NOME`     |
| `)`    | `RPAREN`   |
| `=>`   | `ARROW`    |
| `x`    | `NOME`     |
| `in`   | `IN`       |
| `f`    | `NOME`     |
| `(`    | `LPAREN`   |
| `1`    | `INTEIRO`  |
| `)`    | `RPAREN`   |

Se você ainda não consegue separar bem a responsabilidade de cada etapa do
pipeline, observe aqui que o léxico não sabe nada sobre lambdas: `fn`, `=>` e
`,` são apenas palavras da linguagem independentes umas das outras. Quem sabe
que a frase `fn (x) => x` é um lambda é o parser, não o lexer.

## Bloco 3: Sintaxe

### 3.1 Sintaxe concreta (EBNF)

> Uma observação aqui sobre notação. Lembre que em EBNF, os parênteses `( … )`
> são meta-símbolos usados para indicar agrupamento. Mas agora os parênteses
> também são terminais de nossa linguagem. Para evitar confusão, escreverei os
> parênteses _da linguagem_ como `LPAREN` e `RPAREN`. E todos os demais
> terminais, pros quais não há confusão possível (`let`, `in`, `fn`, `=`, `=>`,
> `,`, `+`, `-`, `*`, `/`, `**`), continuarei denotando de forma literal.
> Assim, os parênteses que aparecem na EBNF são meta-linguagem.

Esta é nossa nova EBNF, derivada diretamente da BNF que definimos na aula
passada. Fiz apenas os pequenos ajustes que aprendemos a fazer, aplicando
regras de "refatoramento de gramáticas" que aprendemos na Aula 06.  

```text
exp     ::= let NOME = exp in exp
          | fn LPAREN [ params ] RPAREN => exp                      ← NOVO
          | termo { ( + | - ) termo }
termo   ::= fator { ( * | / ) fator }
fator   ::= unario [ ** fator ]
unario  ::= [ + | - ] chamada                                       ← ALTERADO
chamada ::= atomo { LPAREN [ args ] RPAREN }                        ← NOVO
atomo   ::= INTEIRO | NOME | LPAREN exp RPAREN
params  ::= NOME { , NOME }                                         ← NOVO
args    ::= exp { , exp }                                           ← NOVO
```

Em relação à gramática de `aljabr-v1` vista na Aula 08, há três mudanças:
1. adicionamos as regras `chamada`, `params` e `args`.
2. `exp` ganhou mais uma produção: o lambda `fn (…) => exp`;
3. a regra `unario` agora se aplica a `chamada` (antes era `atomo`);

> **Pergunta:** a lista de parâmetros `[ params ]` é opcional. Que
> programa isso permite escrever? E por que `args` também aparece entre `[ ]`
> em `chamada`?
>
> Resposta: permite lambdas sem parâmetros, `fn () => 42`, e aplicações sem
> argumentos, `f()`.

### 3.2 Decisões de design embutidas na gramática

Lembre que precedência, associatividade e aridade são decisões de design que
queremos que fiquem codificadas na gramática. Vejamos o que a gramática acima
registra sobre nossas decisões.

**O lambda está no nível de `exp`** (o mesmo de `let` e, portanto, o de menor
precedência). Consequência: o corpo de um lambda se estende o mais à direita
possível.

```text
fn (x) => x + 1          # o corpo desse lambda é  x + 1
                         # NÃO é a soma de um lambda com 1
```

Uma "_consequência da consequência_" é que um lambda só pode atuar como operando
de um operador se for colocado entre parênteses.

```text
1 + fn (x) => x          # erro sintático (tente fazer o parsing)

1 + (fn (x) => x)        # com parênteses, é sintaticamente válido
                         # mas… é um erro semântico somar um número a função

1 + (fn (x) => x)(1)     # sintaticamente ok
                         # mas agora o segundo operando não é mais um lambda
                         # é uma aplicação
```

**A aplicação tem a maior precedência**. Por sinal, a gramática coloca a aplicação
acima até dos operadores unários e de `**`. É a regra `unario ::= [ + | - ] chamada`
que garante isso. Ou seja:

```text
-f(2)       # será tratada como -(f(2))
f(2) ** 2   # será tratada como (f(2)) ** 2
```

**As aplicações se encadeiam à esquerda**. A repetição `{ LPAREN [ args ] RPAREN }`
na regra `chamada` produz uma AST com agrupamento à esquerda, tal como fizemos em
`exp` e `termo`. Assim, temos que:

```text
f(1)(2)     # será tratada como  (f(1))(2)
```

**O corpo na definição e os argumentos na chamada são `exp` completas** Por isso,
podemos escrever chamadas com expressões sem parênteses na posição de argumentos, tais
como `f(x + 2, 5)` ou como `f(let x = 2 in x + 2, 5)` e, por fim, também podemos usar
lambdas como argumentos, também sem parênteses como em: `f(fn (x) => x, 2)`.

**A vírgula não é um operador**. Ela apenas separa parâmetros e argumentos;
`1, 2` não é uma expressão. Por isso `f(1, 2)` é uma aplicação com dois argumentos,
e `f((1, 2))` é um erro sintático: a linguagem não tem tuplas.

**Espaços continuam sendo não significativos.** `f(3)` e `f (3)` são o mesmo programa.

> **Pergunta:** por que a aplicação direta de um lambda exige
> parênteses, em `(fn (x) => x)(1)`?
>
> Resposta: sem eles, `fn (x) => x(1)` seria lido como um lambda cujo corpo é
> `x(1)`: o corpo se estende o máximo possível à direita. Compare as duas ASTs:
>
> ```text
> (fn (x) => x)(1)    App(Lambda(["x"], Var("x")), [Num(1)])
> fn (x) => x(1)      Lambda(["x"], App(Var("x"), [Num(1)]))
> ```

### 3.3 Erros sintáticos e erros semânticos

A gramática não sabe o que é uma função. Por isso:

```text
5(3)
```

é um programa **sintaticamente válido**: `chamada ::= atomo { … }` aceita
qualquer `atomo` seguido de argumentos entre parênteses. Que `5` não seja uma
função só é descoberto na avaliação: é um erro **semântico** (em tempo de
execução). Já os programas abaixo são rejeitados pelo parser:

| Programa                | Por quê                                          |
|-------------------------|--------------------------------------------------|
| `fn x => x`             | faltam os parênteses dos parâmetros              |
| `fn (x,) => x`          | vírgula sem parâmetro seguinte                   |
| `f(1,)`                 | vírgula sem argumento seguinte                   |
| `fn (x) x`              | falta o `=>`                                     |
| `fn (1) => x`           | parâmetro precisa ser `NOME`                     |
| `(fn (x) => x`          | parêntese não fechado                            |
| `1 + fn (x) => x`       | lambda como operando, sem parênteses             |
| `let fn = 1 in fn`      | `fn` é palavra reservada, não pode ser nome      |

### 3.4 Sintaxe abstrata (intencional)

Como na Aula 09, são dois novos tipos de nós na AST. Relembre ainda que parênteses
e vírgulas não aparecem na AST: a própria estrutura da árvore já os codifica. Na
especificação, vamos denotar os novos tipos de nós por:

```text
Lambda(params, corpo)
App(funcao, args)
```

Gramática abstrata ou intencional estendida (compare com a da Aula 08; `n, m ≥ 0`):

```text
exp ::= INTEIRO
      | NOME
      | let NOME = exp₁ in exp₂
      | exp₁ op exp₂                      (op ∈ {+, -, *, /, **})
      | op exp                            (op ∈ {+, -})
      | fn(p₁, …, pₙ) => exp              ← NOVA (Lambda)
      | exp(exp₁, …, expₘ)                ← NOVA (App)
```

Exemplos de sintaxe concreta → sintaxe abstrata (usando a notação da Aula 09;
`Neg` denota o `-` unário):

| Programa                  | AST                                                              |
|---------------------------|------------------------------------------------------------------|
| `fn () => 42`             | `Lambda([], Num(42))`                                            |
| `fn (x, y) => x * x + y`  | `Lambda(["x","y"], Add(Mul(Var("x"), Var("x")), Var("y")))`      |
| `(fn (x) => x)(1)`        | `App(Lambda(["x"], Var("x")), [Num(1)])`                         |
| `f(1)(2)`                 | `App(App(Var("f"), [Num(1)]), [Num(2)])`                         |
| `f(fn (x) => x, 2)`       | `App(Var("f"), [Lambda(["x"], Var("x")), Num(2)])`               |
| `-f(2)`                   | `Neg(App(Var("f"), [Num(2)]))`                                   |
| `f(2) ** 2`               | `Pow(App(Var("f"), [Num(2)]), Num(2))`                           |

> **Questão (quiz?):** a turma conseguirá desenhar a AST
> de `fn (x, y) => x * x + y` como árvore, a partir da gramática?

**Hierarquia de precedência** (da menor para a maior):

| Nível | Construções                                             |
|-------|---------------------------------------------------------|
| 1     | `let`, `fn` (corpo se estende à direita)                |
| 2     | `+` `-` (binários, assoc. à esquerda)                   |
| 3     | `*` `/` (assoc. à esquerda)                             |
| 4     | `**` (assoc. à direita)                                 |
| 5     | `+` `-` (unários)                                       |
| 6     | aplicação `f(…)` (assoc. à esquerda), parênteses        |

