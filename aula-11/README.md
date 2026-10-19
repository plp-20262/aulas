# Aula 11 — Unidade 4 (2/4)

> Tema da aula: especificação formal de `aljabr` v2 (que difere de `v1` pela
> introdução de lambdas e closures). Também apresentarei, mais uma vez, uma
> visão geral de como essa especificação orientará a implementação.


## Objetivo geral

Na Aula 09 decidimos _como escrever_ funções em `aljabr` e vimos,
informalmente, _o que elas devem significar_: um lambda avalia para um **closure**,
uma tripla `(parâmetros, corpo, ambiente de criação)`.

Nesta aula transformamos essas decisões em especificações precisas, nos três
níveis a que você já deve estar acostumado: **léxico** (REGEX), **sintático** (EBNF) e
**semântica** (regras de avaliação `⟨e, ρ⟩ ⇓ v`). Também veremos como cada
especificação orienta a implementação do estágio correspondente do pipeline.

> IMPORTANTE: a implementação de referência de `aljabr` v2 só será apresentada
> no início da Aula 12. Até lá, tente implementar a linguagem você mesmo, a
> partir das especificações desta aula (ver exercícios). É assim que se
> aprende a ler especificações.


## Roteiro da aula (tempos indicativos)

| Bloco | Conteúdo                                         | Tempo  |
|-------|--------------------------------------------------|--------|
| 1     | Retomada e o que muda no pipeline                | 10 min |
| 2     | Léxico: novos tokens                             | 10 min |
| 3     | Sintaxe: EBNF e sintaxe abstrata                 | 25 min |
| 4     | Semântica: domínios e regras de avaliação        | 30 min |
| 5     | Derivações e propriedades                        | 20 min |
| 6     | Da especificação à implementação (visão geral)   | 15 min |
| 7     | Prévia de escopo dinâmico e fechamento           | 10 min |


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

Se você ainda não consegue separar bem a responsabilidade de cada etapa do pipeline,
observe aqui que o léxico não sabe nada sobre lambdas: `fn`, `=>` e `,` são apenas
palavras da linguagem independentes umas das outras. Quem sabe que a frase `fn (x) => x`
é um lambda é o parser, não o lexer.

## Bloco 3: Sintaxe

### 3.1 Sintaxe concreta (EBNF)

> Uma observação sobre notação. Lembre que em EBNF, os parênteses `( … )` são
> meta-símbolos usados para indicar agrupamento. Mas agora os parênteses
> também são terminais de nossa linguagem. Para evitar confusão, escreverei
> os parênteses _da linguagem_ como `LPAREN` e `RPAREN`. E todos os demais
> terminais, pros quais não há confusão possível (`let`, `in`, `fn`, `=`,
> `=>`, `,`, `+`, `-`, `*`, `/`, `**`), continuarei denotando de forma
> literal.

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

Em relação à gramática de `aljabr-v1` vista na Aula 08, são três mudanças:
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

### 3.4 Sintaxe abstrata

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
      | fn (p₁, …, pₙ) => exp             ← NOVA (Lambda)
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


## Bloco 4: Semântica

### 4.1 Domínios semânticos

Até a versão `v1` de `aljabr`, temos os seguintes domínios semânticos: _números_, que são
os valores principais sobre os quais queremos computações; _valores_ que combina os números
e o valor `erro` formando o conjunto de valores que podem; e _ambientes_ que é o conjunto
dos possíveis mapeamentos de valores de variáveis a valores. Para a versão `v2`, com a 
inclusão de lambdas e aplicações, precisaremos de duas mudanças: 1) adicionar o
conjunto de _closures_ $\mathrm{Clo}$, que são os valores propriamente ditos dos lambdas
durante a avaliação (ou execução); e 2) atualizar o conjunto de _valores_ $\mathrm{Val}$,
para incluir os _closures_.

| Domínio                                                                          | Descrição                                           |
|----------------------------------------------------------------------------------|-----------------------------------------------------|
| $ℝ$                                                                              | Os números reais.                                   |
| $\mathrm{Clo} = \mathrm{Var}^* \times \mathrm{Exp} \times \mathrm{Env}$          | _Closures_: (parâmetros, corpo, ambiente de criação) |
| $\mathrm{Val} = ℝ ∪ \mathrm{Clo} ∪ \\{ \mathtt{erro} \\}$                        | Valores possíveis                                   |
| $\mathrm{Env} = \mathrm{Var} ⇀ \mathrm{Val}$                                     | Ambientes                                           |

Escreveremos um closure como $\mathsf{clo}((p_1, \ldots, p_n),\, e,\, \rho)$.

> **Nota.** A definição é aparentemente circular: ambientes contêm valores,
> valores incluem closures e closures contêm ambientes. Mas não há problema:
> todo closure contém um ambiente que _já existia_ quando o closure foi criado
> (o ambiente de criação). Closures são, portanto, construídos "de dentro para
> fora". Guarde essa observação: ela volta quando falarmos de recursão.

**Notação.** Para vincular vários parâmetros de uma vez, usaremos a extensão
sucessiva do ambiente:

$$
\rho[p_1 \mapsto v_1, \ldots, p_n \mapsto v_n]
= (\cdots(\rho[p_1 \mapsto v_1])[p_2 \mapsto v_2] \cdots)[p_n \mapsto v_n]
$$

Como antes, é um **novo** ambiente: `ρ` não é modificado.

### 4.2 Regras que já conhecemos

As regras abaixo não mudam. Elas foram repetidas aqui apenas para que este
arquivo seja autocontido. Duas ressalvas: 1) usamos o ambiente _lifted_, o que
nos permite dispensar a regra (VarNaoLigada) vista da Aula 08 (lembre que na
ocasião comentei isso em sala de aula; que usar o ambiente _lifted_ permite
simplificar as regras de derivação); e 2) adotamos uma convenção para a
propagação de erros.)

$$
\frac{}{\langle n, \rho \rangle \Downarrow n} \quad \text{(Num)}
\qquad
\frac{\rho(x) = v}{\langle x, \rho \rangle \Downarrow v} \quad \text{(Var)}
$$

$$
\frac{
  \langle e_1, \rho \rangle \Downarrow v_1 \qquad
  \langle e_2, \rho[x \mapsto v_1] \rangle \Downarrow v_2
}{
  \langle \text{let } x = e_1 \text{ in } e_2, \rho \rangle \Downarrow v_2
} \quad \text{(Let)}
$$

$$
\frac{
  \langle e_1, \rho \rangle \Downarrow v_1 \qquad
  \langle e_2, \rho \rangle \Downarrow v_2
}{
  \langle e_1 \text{ op } e_2, \rho \rangle \Downarrow f_{\mathrm{op}}^{\uparrow}(v_1, v_2)
} \quad \text{(Op)}
$$

(As regras dos operadores unários são análogas.) Lembre que $f^{\uparrow}$ é o
_lift_ da operação parcial $f$:

$$
f^{\uparrow}(v_1, v_2) =
\begin{cases}
f(v_1, v_2) & \text{se } v_1, v_2 \in ℝ \text{ e } (v_1, v_2) \in \mathrm{dom}(f) \\
\mathtt{erro} & \text{caso contrário}
\end{cases}
$$

> **Observe:** como $\mathrm{Val}$ agora inclui closures, o "caso contrário"
> do _lift_ cobre também as operações aritméticas aplicadas a funções. Não
> precisaremos de nenhuma regra nova para `q + 1` quando `q` for uma função: o
> _lift_ que já tínhamos produz `erro`.

**Ambiente _lifted_.** Como na Aula 08, usamos uma versão _lifted_ de `ρ`: para
toda variável `x ∉ dom(ρ)`, definimos `ρ(x) = erro`. Assim, a regra ($\mathrm{Var}$)
cobre também as variáveis não vinculadas, e não precisamos de uma regra à parte para
isso.

**Convenção de propagação de erro.** As regras desta unidade descrevem apenas
o caso em que as premissas produzem valores "de verdade" (elementos de
$ℝ ∪ \mathrm{Clo}$). Para os demais casos, adotamos uma convenção, declarada
uma única vez, válida para todas as regras:

> se alguma premissa da forma $⟨e, ρ⟩ ⇓ v$ produz $v = \mathbf{erro}$, a regra
> não se aplica e a conclusão é $\mathbf{erro}$.

A convenção abrevia as regras de propagação que escrevíamos uma a uma na Aula
07 (`ErrEsq` e `ErrDir`), uma para cada construção. Ela é o equivalente formal
do tratamento monádico de erros da implementação: o erro interrompe a
avaliação assim que aparece (erros são **estritos**). Em particular,
`let x = 1/0 in 5` vale `erro`, e não `5`.

Sobram, portanto, apenas as regras em que um erro **nasce** da própria
construção, e não de uma operação (para as operações, o _lift_ já cuida disso).
É o caso da aplicação, que veremos a seguir.

### 4.3 Novas regras de avaliação

**Criação de closure.** Um lambda avalia para um closure que "congela" o
ambiente corrente:

$$
\frac{}{
  \langle \texttt{fn}\ (p_1, \ldots, p_n) \Rightarrow e,\ \rho \rangle
  \Downarrow
  \mathsf{clo}((p_1, \ldots, p_n),\ e,\ \rho)
} \quad \text{(Lam)}
$$

**Aplicação.** Este é o coração da aula:

$$
\frac{
  \begin{matrix}
  \langle e_f, \rho \rangle \Downarrow \mathsf{clo}((p_1, \ldots, p_n), e_b, \rho_0) \\
  \rule{0pt}{6ex}
  \langle a_i, \rho \rangle \Downarrow v_i \quad (1 \le i \le n) \\
  \rule{0pt}{6ex}
  \langle e_b, \rho_0[p_1 \mapsto v_1, \ldots, p_n \mapsto v_n] \rangle \Downarrow v \\
  \rule{0pt}{3ex}
  \end{matrix}
}{
  \langle e_f(a_1, \ldots, a_n), \rho \rangle \Downarrow v
} \quad \text{(App)}
$$

**Leitura da regra (App)**:

Relembre que para ler regras de derivação é conveniente ler primeiro a regra da conclusão
(parte abaixo da linha), para sabermos o que queremos calcular. A conclusão indica qual é
a forma da expressão para a qual queremos saber o significado (ou resultado). E as premissas,
condições expressas acima da linha, determinam tudo o que precisamos garantir para ter o
direito de aceitar a conclusão.

Neste caso, a conclusão indica que a regra nos permitirá saber como avaliar uma expressão
na forma $e_f(a_1, \ldots, a_n)$ em um momento da computação em que o ambiente é $\rho$. Em
particular, poderemos aceitar que o significado ou o valor resultante da expressão é $v$.
Para isso, precisamos garantir que as premissas (condições acima da linha) sejam verdadeiras.
Nesta regra são exigidas três condições gerais.

A primeira premissa: $\langle e_f, \rho \rangle \Downarrow \mathsf{clo}((p_1, \ldots, p_n),
e_b, \rho_0)$ exige que a expressão que queremos aplicar, $e_f$, seja avaliada para um closure
no mesmo ambiente $\rho$ em que se quer fazer a aplicação. Ou seja, essa condição da regra
exige que $e_f$ expresse uma função. Relembre, contudo, que uma função é um _closure_: uma
tripla $\mathsf{clo}((p_1, \ldots, p_n), e_b, \rho_0)$ que consiste em uma sequência de
parâmetros $(p_1, \ldots, p_n)$, uma expressão $e_b$ e um ambiente de próprio (obtido da
definição do lambda) $\rho_0$. Observe que a premissa exige que haja exatamente $n$ parâmetros
que é exatamente o mesmo número $n$ de argumentos na aplicação (veja a forma da conclusão).

A segunda premissa: $\langle a_i, \rho \rangle \Downarrow v_i \quad (1 \le i \le n)$ é, na
verdade, um conjunto de $n$ premissas. Elas exigem que as $n$ expressões $a_i$
usadas como argumentos de chamada de $e_f$ sejam avaliadas para os valores $v_i$, no
mesmo ambiente $\rho$ em que está sendo feita a aplicação da conclusão.

Por fim, a terceira premissa: $\langle e_b, \rho_0[p_1 \mapsto v_1, \ldots, p_n \mapsto v_n]
\rangle \Downarrow v$ exige que a avaliação do corpo do closure $e_b$ seja avaliado para $v$,
no ambiente de criação do closure $\rho_0$ em que os parâmetrso $p_i$ tenham sido mapeados
para os valores $v_i$ a que correspondem os argumentos de chamada.

Em resumo, podemos dizer que a regra determina que, para avaliar a chamada de função $e_f(a_1, a_2, \ldots a_n)$, é 
necessário: 1) que a expressão $e_f$ seja avaliada para uma função (um closure, mais
especificamente); e 2) que os argumentos $a_i$ sejam avaliados para os valores $v_i$;
e 3) que o resultado da chamada da função $e_f(\ldots)$ será o valor da avaliação do corpo da função,
no ambiente próprio da função, com os valores dos parâmetros mapeados pros valores $v_i$.

> **Pergunta:** na regra (App), em qual ambiente é avaliada cada uma das
> três premissas?
>
> Resposta: a primeira e a segunda, em `ρ` (ambiente de chamada). A terceira,
> em `ρ₀[…]` (ambiente de criação estendido). É exatamente essa diferença que
> explica por que `soma_n(3)` vale `10` e não `103`.

A regra operacional, informal dada na Aula 09 (Seção 4.5) está toda aqui:

| Passo na Aula 09                           | Onde está na formalização                                            |
|--------------------------------------------|----------------------------------------------------------------------|
| 1. avaliar `f` em `ρ` ⟹ closure           | 1ª premissa de (App); (AppNaoFuncao) se não for closure              |
| 2. se `m ≠ n`, erro de aridade             | (AppAridade)                                                         |
| 3. avaliar cada `aᵢ` em `ρ` ⟹ `vᵢ`        | 2ª premissa de (App); erro em algum `aᵢ` ⟹ convenção de propagação  |
| 4. avaliar corpo em `ρ₀[p₁ ↦ v₁, …]`       | 3ª premissa de (App)                                                 |

### 4.4 Regras de erro da aplicação

Há duas maneiras de uma aplicação **originar** um erro, uma por regra. Os erros
que apenas se _propagam_ (um argumento que avalia para `erro`, ou um corpo que
resulta em `erro`) não precisam de regra própria: são cobertos pela convenção
da Seção 4.2 e pela própria regra (App), cujo valor é o valor do corpo.

**Aplicar algo que não é função:**

$$
\frac{
  \langle e_f, \rho \rangle \Downarrow v_f \qquad v_f \notin \mathrm{Clo}
}{
  \langle e_f(a_1, \ldots, a_m),\ \rho \rangle \Downarrow \mathbf{erro}
} \quad \text{(AppNaoFuncao)}
$$

**Número errado de argumentos:**

$$
\frac{
  \langle e_f, \rho \rangle \Downarrow \mathsf{clo}((p_1, \ldots, p_n),\ e_b,\ \rho_0)
  \qquad m \neq n
}{
  \langle e_f(a_1, \ldots, a_m),\ \rho \rangle \Downarrow \mathbf{erro}
} \quad \text{(AppAridade)}
$$

Observe duas escolhas de projeto:

- a **aridade é verificada antes** de avaliar os argumentos (passo 2 antes do
  passo 3 da Aula 09);
- `erro` não pode ser passado como argumento: um argumento que avalia para
  `erro` interrompe a aplicação, pela convenção de propagação da Seção 4.2. Assim,
  as três regras de aplicação, (App), (AppNaoFuncao) e (AppAridade), são
  mutuamente exclusivas.

### 4.5 Erros em ação

| Programa                                  | Resultado | Por quê                                                        |
|-------------------------------------------|-----------|----------------------------------------------------------------|
| `5(3)`                                    | `erro`    | (AppNaoFuncao): `5` não é closure                              |
| `let f = fn (x, y) => x + y in f(1)`      | `erro`    | (AppAridade): 2 parâmetros, 1 argumento                        |
| `let q = fn (x) => x in q + 1`            | `erro`    | (Op) com _lift_: closure não pertence a ℝ                      |
| `let f = fn (x) => x + y in f(1)`         | `erro`    | `ρ(y) = erro` (ρ lifted), propagado por (Op), só na chamada    |
| `let f = fn (x) => x + y in 10`           | `10`      | (Lam) não avalia o corpo; ninguém procurou `y`                 |
| `let x = 1/0 in 5`                        | `erro`    | convenção: a 1ª premissa de (Let) avalia para `erro`           |
| `(fn (x) => 5)(1/0)`                      | `erro`    | convenção: o argumento avalia para `erro`                      |

Os dois programas com `y` merecem atenção. Na primeira forma, `y` é uma
variável livre que não está em lugar nenhum. A lambda foi criada normalmente e
só quando o corpo é avaliado, na chamada, o erro aparece. Na segunda forma, a
lambda nunca é chamada e o programa vale `10`. **Criar uma função não executa o
seu corpo.**

Os dois últimos ilustram a convenção de propagação: o erro interrompe a
avaliação mesmo quando o valor com erro não seria usado (o resultado `5` não
depende de `x`). É o que significa dizer que os erros são estritos.


## Bloco 5: Derivações e propriedades

> Como na Aula 08, as derivações abaixo estão em árvore indentada: a conclusão
> na raiz e as premissas como filhos, na ordem em que aparecem na regra. As
> condições laterais (como `ρ(x) = v`) são folhas rotuladas.

### 5.1 Exemplo 1: `let quad = fn (x) => x * x in quad(3) + quad(5)`

```text
⟨let quad = fn (x) => x * x in quad(3) + quad(5), ∅⟩ ⇓ 34   (Let)
├─ ⟨fn (x) => x * x, ∅⟩ ⇓ Q                                 (Lam)
│     onde Q = clo((x), x * x, ∅)
└─ ⟨quad(3) + quad(5), ρ₁⟩ ⇓ 34                             (Op)
   │     onde ρ₁ = ∅[quad ↦ Q]
   ├─ ⟨quad(3), ρ₁⟩ ⇓ 9                                     (App)
   │  ├─ ⟨quad, ρ₁⟩ ⇓ Q                                     (Var)
   │  │  └─ ρ₁(quad) = Q                                    (acesso ao ambiente)
   │  ├─ ⟨3, ρ₁⟩ ⇓ 3                                        (Num)
   │  └─ ⟨x * x, ∅[x ↦ 3]⟩ ⇓ 9                              (Op)
   │     ├─ ⟨x, ∅[x ↦ 3]⟩ ⇓ 3                               (Var)
   │     │  └─ ∅[x ↦ 3](x) = 3                              (acesso ao ambiente)
   │     ├─ ⟨x, ∅[x ↦ 3]⟩ ⇓ 3                               (Var)
   │     │  └─ ∅[x ↦ 3](x) = 3                              (acesso ao ambiente)
   │     └─ *↑(3, 3) = 9                                    (operação semântica)
   ├─ ⟨quad(5), ρ₁⟩ ⇓ 25                                    (App)
   │  └─ ⋯ análoga à anterior, com x ↦ 5
   └─ +↑(9, 25) = 34                                        (operação semântica)
```

Observe que o corpo `x * x` é avaliado duas vezes, uma para cada aplicação,
cada vez em um ambiente diferente (`x ↦ 3` e `x ↦ 5`). Foi exatamente isso que
buscávamos ao abstrair a _computação_: uma única definição, vários usos.

### 5.2 Exemplo 2: `soma_n(3)` vale `10`

```text
let n = 7 in
let soma_n = fn (x) => x + n in
let n = 100 in
soma_n(3)
```

```text
⟨let n = 7 in … soma_n(3), ∅⟩ ⇓ 10                          (Let)
├─ ⟨7, ∅⟩ ⇓ 7                                               (Num)
└─ ⟨let soma_n = fn (x) => x + n in … soma_n(3), ρ₁⟩ ⇓ 10   (Let)
   │     onde ρ₁ = ∅[n ↦ 7]
   ├─ ⟨fn (x) => x + n, ρ₁⟩ ⇓ S                             (Lam)
   │     onde S = clo((x), x + n, ρ₁)
   └─ ⟨let n = 100 in soma_n(3), ρ₂⟩ ⇓ 10                   (Let)
      │     onde ρ₂ = ρ₁[soma_n ↦ S]
      ├─ ⟨100, ρ₂⟩ ⇓ 100                                    (Num)
      └─ ⟨soma_n(3), ρ₃⟩ ⇓ 10                               (App)
         │     onde ρ₃ = ρ₂[n ↦ 100]
         ├─ ⟨soma_n, ρ₃⟩ ⇓ S                                (Var)
         │  └─ ρ₃(soma_n) = S                               (acesso ao ambiente)
         ├─ ⟨3, ρ₃⟩ ⇓ 3                                     (Num)
         └─ ⟨x + n, ρ₁[x ↦ 3]⟩ ⇓ 10                         (Op)
            │     onde ρ₁[x ↦ 3] = { n ↦ 7, x ↦ 3 }
            ├─ ⟨x, ρ₁[x ↦ 3]⟩ ⇓ 3                           (Var)
            │  └─ ρ₁[x ↦ 3](x) = 3                          (acesso ao ambiente)
            ├─ ⟨n, ρ₁[x ↦ 3]⟩ ⇓ 7                           (Var)
            │  └─ ρ₁[x ↦ 3](n) = 7                          (acesso ao ambiente)
            └─ +↑(3, 7) = 10                                (operação semântica)
```

Compare esta árvore com o rastreamento passo a passo da Aula 09 (§4.6). É a
mesma história, agora escrita com regras:

- a lambda foi avaliada em `ρ₁` e o closure `S` guardou `ρ₁` (onde `n ↦ 7`);
- a aplicação aconteceu em `ρ₃` (onde `n ↦ 100`), e `ρ₃` foi usado para
  encontrar `soma_n` e avaliar o argumento `3`;
- o corpo, contudo, foi avaliado em `ρ₁[x ↦ 3]`, e não em `ρ₃[x ↦ 3]`.

### 5.3 Exemplo 3: um closure criado por outro closure

`(fn (x) => fn (y) => x + y)(2)(3)`, que já vimos na Aula 09 (§6.2).

```text
⟨(fn (x) => fn (y) => x + y)(2)(3), ∅⟩ ⇓ 5   (App)
├─ ⟨(fn (x) => fn (y) => x + y)(2), ∅⟩ ⇓ C   (App)
│  │     onde C = clo((y), x + y, ∅[x ↦ 2])
│  ├─ ⟨fn (x) => fn (y) => x + y, ∅⟩ ⇓ L     (Lam)
│  │     onde L = clo((x), fn (y) => x + y, ∅)
│  ├─ ⟨2, ∅⟩ ⇓ 2                             (Num)
│  └─ ⟨fn (y) => x + y, ∅[x ↦ 2]⟩ ⇓ C        (Lam)
├─ ⟨3, ∅⟩ ⇓ 3                                (Num)
└─ ⟨x + y, ∅[x ↦ 2][y ↦ 3]⟩ ⇓ 5              (Op)
   ├─ ⟨x, ∅[x ↦ 2][y ↦ 3]⟩ ⇓ 2               (Var)
   │  └─ ∅[x ↦ 2][y ↦ 3](x) = 2              (acesso ao ambiente)
   ├─ ⟨y, ∅[x ↦ 2][y ↦ 3]⟩ ⇓ 3               (Var)
   │  └─ ∅[x ↦ 2][y ↦ 3](y) = 3              (acesso ao ambiente)
   └─ +↑(2, 3) = 5                           (operação semântica)
```

Observe o closure `C`: ele foi criado quando `x` valia `2` e carrega essa
informação em seu ambiente de criação. Quando `C` é aplicado a `3`, o corpo
`x + y` encontra `x` (vindo de `ρ₀`) e `y` (vindo do argumento). Sem a captura
do ambiente, a lambda interna não poderia ser avaliada: o `x` teria
desaparecido junto com a aplicação que o ligou.

### 5.4 Exemplos de erro

Aplicando algo que não é função:

```text
⟨let a = 3 in a(4), ∅⟩ ⇓ erro   (Let)
├─ ⟨3, ∅⟩ ⇓ 3                   (Num)
└─ ⟨a(4), ρ₁⟩ ⇓ erro            (AppNaoFuncao)
   │     onde ρ₁ = ∅[a ↦ 3]
   ├─ ⟨a, ρ₁⟩ ⇓ 3               (Var)
   │  └─ ρ₁(a) = 3              (acesso ao ambiente)
   └─ 3 ∈ ℝ                     (condição lateral)
```

Número errado de argumentos:

```text
⟨let f = fn (x, y) => x + y in f(1), ∅⟩ ⇓ erro   (Let)
├─ ⟨fn (x, y) => x + y, ∅⟩ ⇓ F                   (Lam)
│     onde F = clo((x, y), x + y, ∅)
└─ ⟨f(1), ρ₁⟩ ⇓ erro                             (AppAridade)
   │     onde ρ₁ = ∅[f ↦ F]
   ├─ ⟨f, ρ₁⟩ ⇓ F                                (Var)
   │  └─ ρ₁(f) = F                               (acesso ao ambiente)
   └─ 1 ≠ 2                                      (condição lateral: nº de argumentos ≠ nº de parâmetros)
```

### 5.5 Propriedades

- **Determinismo.** Continua valendo para as novas regras: (App),
  (AppNaoFuncao) e (AppAridade) são mutuamente exclusivas, pois cada uma
  depende do valor de `e_f` e do número de argumentos. (E, pela convenção de
  propagação, as regras só se aplicam quando as premissas não produzem `erro`;
  os casos com erro têm uma única conclusão possível.)

- **Escopo léxico.** O valor de uma aplicação depende do closure e dos valores
  dos argumentos, **não** do ambiente em que a aplicação ocorre (além de ser
  nele que se encontram `f` e os argumentos). Foi isso que vimos no Exemplo 2:
  mudar `n` _depois_ de criar `soma_n` não afeta `soma_n`.

- **Funções ainda não podem chamar a si mesmas.** O `let` continua não
  recursivo (Aula 08): em `let f = e₁ in e₂`, `e₁` é avaliada em `ρ`, onde `f`
  ainda não existe. Logo, o closure de `f` não captura `f`:

  ```text
  let f = fn (n) => f(n) in f(1)     # erro: variável 'f' não vinculada
  ```

  Guarde essa limitação: voltaremos a ela.

- **Pureza.** Continuamos sem mutação: o único modo de alterar um ambiente é
  criar um novo, estendendo o anterior.


## Bloco 6: Da especificação à implementação

> Nesta seção, apenas o mapa. A implementação de referência será apresentada
> no início da Aula 12. Use este mapa para implementar você mesmo.

### 6.1 Léxico → lexer

| Especificação                          | Implementação                                             |
|----------------------------------------|-----------------------------------------------------------|
| três novas categorias léxicas          | três novos tipos de token e três novas entradas na lista de regras |
| `=>` antes de `=`                      | posição de `ARROW` na lista, antes de `EQUAL`             |
| `fn` é palavra reservada               | nova entrada no mapa de palavras reservadas               |

### 6.2 EBNF → parser

Relembre a correspondência entre EBNF e funções do parser (Aulas 04 e 05):

| Na EBNF         | Parser descendente recursivo                                  |
|-----------------|---------------------------------------------------------------|
| `{ X }`         | `while` o próximo token pode iniciar `X`                      |
| `[ X ]`         | `if` o próximo token pode iniciar `X`                         |
| terminal `T`    | `expect(T)`                                                   |
| não-terminal    | chamada à função correspondente                               |

E o que muda nas regras da gramática:

| Regra                       | Função do parser                                         |
|-----------------------------|----------------------------------------------------------|
| `exp` (alternativa `fn`)    | em `parse_exp`: se o próximo token é `FN`, chama `parse_lambda` |
| `params`                    | nova: `parse_params`                                     |
| `args`                      | nova: `parse_args`                                       |
| `chamada`                   | nova: `parse_chamada`                                    |
| `unario`                    | passa a chamar `parse_chamada` em vez de `parse_atomo`   |

Como exemplo da derivação mecânica, eis o pseudo-código de `parse_chamada`:

```python
def parse_chamada(stream):
    """chamada ::= atomo { LPAREN [ args ] RPAREN }"""
    ast = parse_atomo(stream)
    while peek(LPAREN):               # { … } vira while
        expect(LPAREN)
        args = []
        if not peek(RPAREN):          # [ … ] vira if
            args = parse_args(stream)
        expect(RPAREN)
        ast = App(ast, args)          # agrupamento à esquerda: f(1)(2) = (f(1))(2)
    return ast
```

As funções `parse_lambda`, `parse_params` e `parse_args` seguem o mesmo método
(ficam como exercício). A gramática continua sendo LL(1): `FN` decide a
alternativa de `exp`; `NOME` ou `RPAREN` decidem se há `params` ou `args`; e
um `LPAREN` logo após um `atomo` só pode iniciar uma aplicação.

> **Questão de projeto (pense antes de implementar):** a AST que construímos
> até aqui é feita de listas, e o `eval` decide qual regra aplicar olhando a
> forma da lista (seu primeiro elemento e seu tamanho). `Lambda` e `App`
> também podem ter 2 ou 3 componentes. Como evitar que sejam confundidos com
> operadores unários e binários?

### 6.3 Regras de avaliação → eval

A assinatura de `eval` não muda: `eval(ast, env) -> Val`. Cada regra vira uma
cláusula. Para a regra (App), leia as premissas como instruções:

| Parte da regra                                            | O que o `eval` faz                                              |
|-----------------------------------------------------------|-----------------------------------------------------------------|
| $\langle e_f, \rho \rangle \Downarrow \mathsf{clo}(\ldots)$ | avalia `e_f` em `env` e verifica que o resultado é um closure   |
| $m \neq n$                                                | compara o número de argumentos com o de parâmetros              |
| $\langle a_i, \rho \rangle \Downarrow v_i$                | avalia cada argumento em `env`, o ambiente **de chamada**       |
| $\rho_0[p_1 \mapsto v_1, \ldots]$                         | cria um novo dicionário a partir do ambiente **do closure**     |
| $\langle e_b, \ldots \rangle \Downarrow v$                | avalia o corpo no novo ambiente e devolve o resultado           |

E para a regra (Lam): empacotar `(params, corpo, env)` em um closure, sem
avaliar o corpo. Um closure é uma tripla; em Python, uma tupla ou uma
`dataclass` imutável com três campos serve bem.

Observe que as regras `AppNaoFuncao` e `AppAridade` correspondem aos dois
pontos em que o `eval` _origina_ um `Erro` na aplicação. Já a propagação de
erro (um argumento, ou o corpo, que resulta em `Erro`) é a convenção da §4.2: o
`eval` apenas devolve o erro recebido, sem prosseguir. E lembre que o _lift_
das operações já trata o caso de funções em expressões aritméticas.

### 6.4 Conjunto de testes

Use os programas abaixo para testar sua implementação.

| Programa                                                           | Resultado |
|--------------------------------------------------------------------|-----------|
| `let quad = fn (x) => x * x in quad(3) + quad(5)`                  | `34`      |
| `(fn (x, y) => x + y)(2, 3)`                                       | `5`       |
| `(fn () => 42)()`                                                  | `42`      |
| `(fn (x) => fn (y) => x + y)(2)(3)`                                | `5`       |
| `let n = 7 in let soma_n = fn (x) => x + n in let n = 100 in soma_n(3)` | `10` |
| `let f = fn (x) => x in -f(2)`                                     | `-2`      |
| `let f = fn (x) => x in f(2) ** 2`                                 | `4`       |
| `let f = fn (x, y) => x + y in f(1)`                               | `erro`    |
| `5(3)`                                                             | `erro`    |
| `let q = fn (x) => x in q + 1`                                     | `erro`    |
| `let f = fn (x) => x + y in 10`                                    | `10`      |
| `let f = fn (x) => x + y in f(1)`                                  | `erro`    |
| `let x = 1/0 in 5`                                                 | `erro`    |
| `(fn (x) => 5)(1/0)`                                               | `erro`    |

E os programas abaixo devem ser **rejeitados pelo parser**:
`fn x => x`, `fn (x,) => x`, `f(1,)`, `fn (x) x`, `1 + fn (x) => x`,
`let fn = 1 in fn`.


## Bloco 7: Prévia de escopo dinâmico e fechamento

### 7.1 Uma diferença de um único símbolo

Na regra (App), o corpo é avaliado em $\rho_0[\ldots]$, o ambiente de criação.
Imagine uma outra regra, idêntica em tudo, exceto por uma letra:

```math
\frac{
  \begin{array}{c}
  \langle e_f, \rho \rangle \Downarrow \mathsf{xclo}((p_1, \ldots, p_n),\ e_b,\ \rho_0) \\
  \rule{0pt}{6ex} \langle a_i, \rho \rangle \Downarrow v_i
  \quad (1 \le i \le n) \\
  \rule{0pt}{6ex} \langle e_b,\ \rho[p_1 \mapsto v_1, \ldots, p_n \mapsto v_n] \rangle \Downarrow v
  \end{array}
}{
  \langle e_f(a_1, \ldots, a_n),\ \rho \rangle \Downarrow v
} \quad \text{(AppDin)}
```

> **Pergunta à turma:** o que mudou? O que passa a acontecer com o programa
> abaixo?
>
> ```text
> let a = 10 in
> let f = fn (x) => x + a in
> let a = 20 in
> f(5)          # (App): 15      (AppDin): 25
> ```
>
> Observe que, com (AppDin), o ambiente `ρ₀` guardado no closure nunca é
> usado. Seria ele ainda necessário?

Essa é a diferença entre escopo **léxico** e escopo **dinâmico**, tema central
da Aula 12. Por ora, registre: `aljabr` usa escopo léxico, e a Aula 12 mostra
o que se perde e o que se ganha com a outra escolha.

### 7.2 Resumo

Nesta aula:

1. especificamos `aljabr` v2 nos três níveis: REGEX (3 novos tokens), EBNF
   (lambda, aplicação, parâmetros e argumentos) e regras de avaliação (closure
   e aplicação);
2. vimos que a regra (App) concentra a decisão de design mais importante da
   unidade: o corpo é avaliado no ambiente **de criação**, estendido com os
   argumentos;
3. vimos como cada especificação se traduz em uma parte da implementação.

### 7.3 Ponte para a Aula 12

Na próxima aula apresento a implementação de referência de `aljabr` v2
(que oficializa a versão). Em seguida, implementamos as duas versões da regra
de aplicação, léxica e dinâmica, lado a lado, e comparamos os resultados.


## Exercícios de fixação

Resolva antes da próxima aula.

1. Tokenize `(fn (x, y) => x + y)(2, 3)`.

2. Desenhe a árvore de sintaxe abstrata de `fn (x) => x + 1 (2)` e de
   `-f(2) ** 2`. O que você observa na primeira? O que acontece quando essa
   lambda é aplicada a um argumento?

3. Faça a derivação, em árvore indentada, de:

   ```text
   let a = 10 in
   let f = fn (x) => x + a in
   f(5)
   ```

4. Para cada programa abaixo, diga o resultado e justifique com base nas
   regras:

   ```text
   a) let x = 1 in
      let f = fn (y) => x + y in
      let g = fn (x) => f(x) in
      g(10)

   b) let x = 10 in (fn (x) => x + 1)(5)

   c) let make = fn (n) => fn (x) => x + n in
      let soma5 = make(5) in
      soma5(3)

   d) let f = fn (n) => f(n) in f(1)
   ```

5. **(Implementação)** Implemente `aljabr` v2 a partir das especificações
   desta aula: lexer, parser e `eval`. Use o conjunto de testes do Bloco 6.4.

   > IMPORTANTE: tente fazer isso você mesmo, antes de olhar a implementação
   > de referência (Aula 12).

6. **(Desafio)** Qual o resultado do programa abaixo? Faça a derivação das
   primeiras aplicações. O que há de diferente em relação aos exemplos da
   aula?

   ```text
   let aplica2 = fn (f, v) => f(f(v)) in
   aplica2(fn (x) => x * x, 3)
   ```

7. **(Discussão)** Na regra (App), $\rho_0[p_1 \mapsto v_1, \ldots, p_n \mapsto
   v_n]$ é uma extensão _sucessiva_. O que significa `fn (x, x) => x`
   aplicada a `(1, 2)`? Que valor sua implementação devolve? Seria melhor
   rejeitar esse programa no parser? Que alternativas de projeto você vê, e o
   que cada uma custa?

8. **(Desafio)** No exercício 4d, o programa dá erro porque `f` não está no
   ambiente do closure. O que precisaria mudar na regra (Let) para que `f`
   pudesse enxergar a si mesma? Que problema aparece ao tentar descrever o
   ambiente de criação desse closure? (Dica: o closure precisaria conter um
   ambiente que contém o próprio closure.)

9. **(Desafio extra)** O lexer de `aljabr` já reconhece o token `?` (entrada de
   dados), mas o parser ainda não o aceita. Estenda a gramática EBNF desta aula
   para incluí-lo e decida onde ele deve ficar na hierarquia de precedência.


## Pontos de checagem de entendimento

Verificar ao longo da aula:

- **Após o Bloco 2:** a turma explica por que `=>` deve preceder `=` na lista
  de regras léxicas?
- **Após o Bloco 3:** a turma desenha a AST de `fn (x, y) => x * x + y` e de
  `f(1)(2)`?
- **Após o Bloco 3:** a turma explica por que `(fn (x) => x)(1)` precisa de
  parênteses?
- **Após o Bloco 4:** a turma identifica, na regra (App), qual premissa usa
  `ρ` e qual usa `ρ₀`?
- **Após o Bloco 4:** a turma distingue erro sintático de erro semântico
  (`fn x => x` vs. `5(3)`)?
- **Após o Bloco 4:** a turma distingue o erro que _nasce_ (`5(3)`, aridade)
  do erro que apenas se _propaga_ (argumento que avalia para `erro`)?
- **Após o Bloco 5:** a turma percebe que criar uma função não executa o seu
  corpo (`let f = fn (x) => x + y in 10`)?
- **Após o Bloco 6:** a turma sabe, para cada estágio, qual especificação
  orienta a implementação?
- **Após o Bloco 7:** a turma percebe que a diferença entre escopo léxico e
  dinâmico é a diferença entre `ρ₀` e `ρ` em uma única premissa?

FIM

