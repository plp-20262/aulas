# O que dá para fazer com `aljabr` v2?

Roteiro de exemplos, do trivial ao surpreendente. Para cada programa:

1. leia o código;
2. **prediga o resultado** antes de executar;
3. só então abra a resposta (`▶ Resposta`) e compare com a execução do interpretador.

> Dica: execute com `python main.py programa.aljabr` ou pela entrada padrão.
> A linguagem não tem comentários, então as explicações ficam fora do código.

---

## Nível 1: Expressões e `let`

### 1.1 Precedência

```text
2 + 3 * 4 ** 2
```

<details>
<summary>▶ Resposta</summary>

**`50`**. O operador `**` tem a maior precedência, depois `*`, depois `+`: 2 + 3 · 16.

</details>

### 1.2 Os valores são números reais

```text
7 / 2
```

<details>
<summary>▶ Resposta</summary>

**`3.5`**. O domínio é ℝ, não os inteiros.

</details>

### 1.3 Sombreamento

```text
let x = 5 in
let x = x * 2 in
x + 1
```

<details>
<summary>▶ Resposta</summary>

**`11`**. O `x` interno *sombreia* o externo, mas sua definição `x * 2` ainda usa o `x` externo (regra (Let): `e1` é avaliada em ρ, e `e2` em ρ[x ↦ v1]).

</details>

---

## Nível 2: Funções e closures

### 2.1 Função com vários parâmetros

```text
let hipotenusa = fn (a, b) => (a * a + b * b) ** (1 / 2) in
hipotenusa(3, 4)
```

<details>
<summary>▶ Resposta</summary>

**`5.0`**. Uma raiz quadrada via `** (1 / 2)`.

</details>

### 2.2 Função que retorna função (primeiro tipo de função de alta ordem)

```text
let soma = fn (n) => fn (x) => x + n in
let soma5 = soma(5) in
soma5(10) + soma(1)(1)
```

<details>
<summary>▶ Resposta</summary>

**`17`** (15 + 2). `soma5` "lembra" que `n = 5` mesmo depois de a chamada `soma(5)` ter terminado: o closure guarda o ambiente de criação. Note também o encadeamento `soma(1)(1)`, permitido pela regra `chamada ::= atomo { ( [args] ) }`.

</details>

### 2.3 Escopo léxico

```text
let n = 7 in
let soma_n = fn (x) => x + n in
let n = 100 in
soma_n(3)
```

<details>
<summary>▶ Resposta</summary>

**`10`**, e não 103. O corpo de `soma_n` é avaliado em ρ₀ (o ambiente *de criação*), onde `n = 7`. O segundo `let n = 100` não afeta o closure. Com a regra hipotética (AppDin) do Bloco 7, o resultado seria 103.

</details>

---

## Nível 3: Funções de alta ordem (outras)

### 3.1 Composição

```text
let compose = fn (f, g) => fn (x) => f(g(x)) in
let inc = fn (x) => x + 1 in
let dobro = fn (x) => x * 2 in
let f = compose(inc, dobro)
let g = compose(dobro, inc)
f(5) + g(5)
```

<details>
<summary>▶ Resposta</summary>

**`23`** (11 + 12). A composição **não** é comutativa: `inc(dobro(5)) = 11`, mas `dobro(inc(5)) = 12`.

</details>

### 3.2 Reaplicando funções: `twice`

```text
let twice = fn (f) => fn (x) => f(f(x)) in
twice(twice)(fn (x) => x * 2)(1)
```

<details>
<summary>▶ Resposta</summary>

**`16`**. `twice(twice)` aplica seu argumento **quatro** vezes (`twice` aplicado duas vezes a `twice`): 1 → 2 → 4 → 8 → 16.

</details>

### 3.3 Método de Newton para calcular √2 (ou método babilônico), sem laços

```text
let twice = fn (f) => fn (x) => f(f(x)) in
let passo = fn (x) => (x + 2 / x) / 2 in
twice(twice(twice(passo)))(1)
```

<details>
<summary>▶ Resposta</summary>

Aproximadamente **`1.4142135623730951`**. Empilhar `twice` três vezes dá 2³ = 8 iterações do passo de Newton, partindo de 1. A última casa decimal depende da aritmética de ponto flutuante.

Iteração de Newton para `a = 2`:
$x_{n+1} = (x_n + 2/x_n)/2$. Converge quadraticamente para √2.

</details>

---

## Nível 4: Booleans "por cima" da linguagem

Nossa linguagem `aljabr` não tem booleans, nem `if` (nem mesmo operadores de comparação, na verdade). Mas **funções são valores**, e isso basta para **definir** ou **codificar** os valores `VERDADE` e `FALSO` como uma pequena biblioteca escrita na própria linguagem. Atenção: aqui estou dizendo que vou adicionar booleans, usando a linguagem que já temos, não que vamos mudar o núcleo da linguagem... ou seja, exatamente como uma "biblioteca" de booleans.

A ideia central: um boolean é uma função que *escolhe* entre duas alternativas. `VERDADE` devolve a primeira; `FALSO` devolve a segunda.

### 4.1 A biblioteca

```text
let VERDADE = fn (t, f) => t in                # esta função é uma codificação do TRUE
let FALSO = fn (t, f) => f in                  # e esta, do FALSE
let not = fn (b) => b(FALSO, VERDADE) in
let and = fn (b1, b2) => b1(b2, FALSO) in
let or = fn (b1, b2) => b1(VERDADE, b2) in
let to_num = fn (b) => b(1, 0) in              # converte pra inteiro (pra poder ser valor final)
```

Lidas como um "se":
- `not(b)` é *se `b` então `FALSO` senão `VERDADE`*;
- `and(a, b)` é *se `a` então `b` senão `FALSO`*;
- `or(a, b)` é *se `a` então `VERDADE` senão `b`*.

Como um programa só produz números, `to_num` converte um boolean em `1` (VERDADE) ou `0` (FALSO), para podermos ver o resultado.

Para usar a biblioteca, escreva uma expressão **depois do último `in`**. Por exemplo, a biblioteca seguida de `to_num(not(FALSO))` é um programa completo.

### 4.2 Prediga o resultado

Cada expressão abaixo vai logo depois da biblioteca.

| # | Expressão |
|---|-----------|
| B1 | `to_num(VERDADE)` |
| B2 | `to_num(not(VERDADE))` |
| B3 | `to_num(and(VERDADE, FALSO))` |
| B4 | `to_num(or(FALSO, VERDADE))` |
| B5 | `to_num(not(and(VERDADE, or(FALSO, FALSO))))` |

<details>
<summary>▶ Respostas</summary>

| # | Resultado | Por quê |
|---|-----------|---------|
| B1 | `1` | `VERDADE(1, 0)` devolve o primeiro argumento. |
| B2 | `0` | `not(VERDADE)` = `VERDADE(FALSO, VERDADE)` = `FALSO`. |
| B3 | `0` | `and(VERDADE, FALSO)` = `VERDADE(FALSO, FALSO)` = `FALSO`. |
| B4 | `1` | `or(FALSO, VERDADE)` = `FALSO(VERDADE, VERDADE)` = `VERDADE`. |
| B5 | `1` | `or(FALSO, FALSO)` = `FALSO`; `and(VERDADE, FALSO)` = `FALSO`; `not(FALSO)` = `VERDADE`. |

Em cada caso, o resultado sai por simples substituição, passo a passo, exatamente como a regra (App) manda: o corpo é avaliado com os parâmetros ligados aos argumentos.

</details>

### 4.3 Um `se` de biblioteca, e uma surpresa

Com booleans como seletores, um "if" é só aplicar o boolean aos dois ramos:

```text
let se = fn (c, t, e) => c(t, e) in
```

Acrescente essa linha à biblioteca e prediga:

| # | Expressão |
|---|-----------|
| S1 | `se(VERDADE, 10, 20)` |
| S2 | `se(FALSO, 10, 20)` |
| S3 | `se(VERDADE, 10, 1 / 0)` |
| S4 | `and(FALSO, 1 / 0)` (compare com `&&` em outras linguagens) |
| S5 | `se(VERDADE, fn () => 10, fn () => 1 / 0)()` |

<details>
<summary>▶ Respostas</summary>

| # | Resultado | Por quê |
|---|-----------|---------|
| S1 | `10` | `VERDADE(10, 20)` escolhe o primeiro. |
| S2 | `20` | `FALSO(10, 20)` escolhe o segundo. |
| S3 | `erro` | **Surpresa!** `aljabr` é estrita: os argumentos são avaliados *antes* da chamada, então `1 / 0` é avaliado mesmo sem ser escolhido, e o erro interrompe a aplicação. |
| S4 | `erro` | Pelo mesmo motivo, `and` implementado como função **não tem curto-circuito**. |
| S5 | `10` | Embrulhar cada ramo em uma função sem parâmetros (um *thunk*) adia a avaliação. `se` devolve o thunk escolhido, e o `()` final chama apenas ele. |

</details>

### 4.4 Para discutir: "por cima" ou "por baixo"?

O que fizemos foi acrescentar booleans **por cima** da linguagem, como uma biblioteca: nenhuma linha do lexer, do parser ou do `eval` mudou. Mais adiante veremos a alternativa de colocá-los **por baixo**, no núcleo da linguagem.

<details>
<summary>▶ Há alguma garantia de que um "boolean" é mesmo um boolean? Prediga: <code>not(fn (a, b) => 42)</code></summary>

Resultado: **`42`**. Qualquer função de dois parâmetros funciona como "boolean", porque `not` só aplica o seu argumento a `FALSO` e `VERDADE`. Já `to_num(5)` dá `erro` (regra (AppNaoFuncao)), e `VERDADE + 1` também (o *lift* só opera sobre ℝ). Ou seja, não há distinção entre booleans e outras funções: o que garantiria isso é um sistema de tipos, assunto de uma aula futura.

</details>

<details>
<summary>▶ O que um `se` no núcleo faz que uma função não consegue?</summary>

Avaliar **apenas o ramo escolhido**. Como funções são estritas, um `se` de biblioteca sempre avalia os dois ramos (ou exige thunks, como em S5). No núcleo, o `se` seria uma construção com sua própria regra de avaliação, e o mesmo vale para `and`/`or` com curto-circuito.

</details>

<details>
<summary>▶ Comparando as duas abordagens</summary>

| | **Por cima** (biblioteca) | **Por baixo** (núcleo) |
|---|---|---|
| Mudança na linguagem | nenhuma | novos tokens, nova EBNF, novos valores e regras |
| Avaliação | estrita: sem curto-circuito | `se`, `and` e `or` podem avaliar só o necessário |
| Representação | booleans são closures; um programa que devolve `VERDADE` mostra um closure | valores `VERDADE` e `FALSO` próprios |
| Erros | `not(5)` e `VERDADE + 1` dão `erro` apenas por acaso | o núcleo pode distinguir booleans de números |
| Custo | o programador paga em thunks | a linguagem fica maior, com mais regras |

</details>


### Para discutir com a turma

<details>
<summary>▶ Por que os booleans são funções?</summary>

`VERDADE(a)(b)` devolve `a` e `FALSO(a)(b)` devolve `b`: um boolean é um *seletor*. Um "if" é simplesmente aplicar o boolean aos dois ramos.

</details>

<details>
<summary>▶ Por que os ramos são `fn () => ...` e há um `()` no final?</summary>

`aljabr` é **estrita**: os argumentos são avaliados antes da chamada. Se passássemos os ramos diretamente, os *dois* seriam avaliados, e o ramo recursivo nunca terminaria. Embrulhar cada ramo em uma função sem parâmetros (um *thunk*) adia a avaliação; o `()` final chama apenas o ramo escolhido.

</details>

<details>
<summary>▶ O que é `z`? Por que não o combinador Y clássico?</summary>

`z` é o combinador de ponto fixo para avaliação **por valor** (combinador Z). No Y clássico, `x(x)` seria avaliado imediatamente e entraria em laço infinito numa linguagem estrita. A eta-expansão `fn (v) => x(x)(v)` atrasa essa avaliação até que a função seja de fato chamada.

</details>

<details>
<summary>▶ Por que `dobrar` é "curried"?</summary>

O combinador `z` só sabe lidar com funções de **um** argumento (a regra (AppAridade) rejeitaria qualquer outra chamada). Por isso `dobrar` recebe `f`, depois `acc`, depois `l`, um de cada vez.

</details>

<details>
<summary>▶ Não temos regra de recursão na especificação. Como a recursão funciona?</summary>

Closures com escopo léxico e a regra (App) já são suficientes para expressar recursão, via ponto fixo. Fica a pergunta para a próxima aula: se não é necessário, por que linguagens reais incluem `letrec`? (Legibilidade, eficiência, e porque o combinador Z é difícil de escrever e de ler.)

</details>

---

## Quando algo dá errado: `erro`

Preveja o resultado de cada programa:

| # | Programa |
|---|----------|
| E1 | `let f = fn (x, y) => x + y in f(1)` |
| E2 | `5(3)` |
| E3 | `let q = fn (x) => x in q + 1` |
| E4 | `let f = fn (x) => x + y in 10` |
| E5 | `let f = fn (x) => x + y in f(1)` |
| E6 | `(fn (x) => 5)(1/0)` |

<details>
<summary>▶ Respostas</summary>

| # | Resultado | Por quê |
|---|-----------|---------|
| E1 | `erro` | (AppAridade): 1 argumento para 2 parâmetros. |
| E2 | `erro` | (AppNaoFuncao): `5` não é um closure. |
| E3 | `erro` | O *lift* das operações aritméticas só é definido sobre ℝ; funções caem no "caso contrário". |
| E4 | `10` | O corpo de uma função **não é avaliado** na criação do closure; a variável `y` livre só importa se a função for chamada. |
| E5 | `erro` | Agora o corpo é avaliado, e `y` não está vinculada. |
| E6 | `erro` | Erros são **estritos**: um argumento que avalia para `erro` interrompe a aplicação, mesmo que a função ignore o parâmetro. |

</details>

---

## Duas curiosidades

<details>
<summary>▶ Quanto vale <code>-2 ** 2</code>?</summary>

**`4`**, e não −4 como na convenção da matemática. Na EBNF, `fator ::= unario [ ** fator ]` e `unario ::= [ + | - ] chamada`, então o `-` se liga ao `2` *antes* do `**`, e a expressão é lida como `(-2) ** 2`. A gramática determina a semântica; mudar o resultado exige mudar a gramática.

</details>

<details>
<summary>▶ E o programa Ω?</summary>

```text
(fn (x) => x(x))(fn (x) => x(x))
```

É um programa válido que **não tem valor**: a regra (App) nunca termina. Como `aljabr` não tem uma forma de detectar isso, o interpretador em Python vai estourar a pilha (`RecursionError`) em vez de produzir `erro`. Um bom gancho para falar sobre não terminação: a semântica big-step simplesmente não tem derivação para esse programa.

</details>

---

## Exercícios propostos

1. Defina `fatorial` usando `z` e os numerais de Church (ou números nativos, com booleans de Church e thunks). Qual o valor de `fatorial(5)`?
2. Escreva `filtrar(p)(lista)` usando `dobrar`.
3. Escreva uma função `comprimento` para listas.
4. Defina `curry` e `uncurry` para funções de dois argumentos.
5. Qual o resultado de `twice(twice)(twice)(fn (x) => x + 1)(0)`? Justifique sem executar.

> **Nota ao professor:** os exemplos do Nível 5 aninham muitas chamadas. Se o interpretador estourar a pilha, aumente o limite com `sys.setrecursionlimit(10000)` no `main`.

