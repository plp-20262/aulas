# Aula 09,  Funções e closures (parte 1/4)

Estágio 4 (parte 1/4)

## Objetivo geral

Introduzir funções, mais especificamente lambdas, como um novo tipo de valor em
nossa LP atual `aljabr`. Passaremos por lambdas fechados (sem variáveis
livres), depois para lambdas com variáveis livres e, portanto, precisaremos
definir o conceito de **closure**. Além desses conceitos, a aula deve
apresentar/retomar o conceito de escopo (léxico, em particular) e ambientes
(como contrapartida runtime).


## Retomando da aula anterior

Na aula anterior, vimos a introdução de variáveis e da expressão `let`. Retomar
a discussão de por que é uma _expressão_.

## Bloco 1: Retomada e problema

### 1.1 Retomada do `let`

Recapitular o que a Aula 08 entregou:

```text
let a = 3 in
let b = 4 in
a * a + b * b
```

Pergunta: *o que o `let` que implementanos na aula passada faz?*  

Resposta: nomeia **valores** para reuso dentro de um escopo. Ou seja, introduz
um potencial inicial de _abstração_ na linguagem. Permite abstrair valores já
calculados, dando-lhes nomes que nos permite reusá-los.


### 1.2 A limitação

A abstração adicionada por `let` é real. Ela permite reusar valores calculados
anteriormente, através dos nomes que introduzimos. Por isso, os armazenamos em
um _ambiente_ e podemos escrever expressões que fazem referências a eles. Mas a
abstração só chega até esse ponto: permite a _abstração de valores_, não
permite a _abstração de computações_.

Para isso, o que precisamos é poder expressar algo como:

```text
quad = "elevar ao quadrado"
quad 3 --> 9
quad 5 --> 25
```

Mas o `let` só permite nomear valores já calculados:

```text
let quad = 3 * 3 in ...   # só funciona para 3
```

Se quisermos `quad de 5`, precisamos escrever `5 * 5` de novo.

**Conclusão:** apenas com `let` não temos como abstrair a **computação**, a
linguagem só nos permite abstrair o **resultado**.


### 1.3 Pergunta central do Estágio 4

> **Como abstrair a própria computação, e não apenas o resultado?**


## Bloco 2:  Decisão de design: a sintaxe

**Este bloco é, em si, conteúdo da aula.** A decisão é da turma.

### 2.1 Critérios de avaliação

1. **Ancoragem léxica**,  o parser reconhece a lambda pelo primeiro token?
2. **Familiaridade**,  lembra funções de LPs convencionais?
3. **Espaço para tipos**,  acomoda anotações futuras sem ginástica?
4. **Preservação de `[` `]`**,  deixa `[` `]` livres para listas depois?
5. **Legibilidade na aplicação**,  quão limpa é a aplicação direta?

### 2.2 As candidatas

| # | Forma              | Ancoragem                         | Familiaridade                         | Tipos                                  | `[` `]`            | Aplicação          |
|---|--------------------|-----------------------------------|---------------------------------------|----------------------------------------|--------------------|--------------------|
| A | `fn (x, y) => exp` | ✅ `fn`                           | ✅ alta (JS-like)                     | ✅ `fn (x: int) : int => ...`          | ✅ livre           | precisa parênteses |
| B | `[x, y] => exp`    | ⚠️ `[` (frágil se listas chegarem) | ⚠️ média                               | ✅ `[x: int, y: float] => ... : float` | ❌ compromete      | precisa parênteses |
| C | `[x, y => exp]`    | ✅ `[`                            | ⚠️ baixa                               | ❌ interação ruim com tipo de retorno  | ❌ compromete      | **sem parênteses** |
| D | `(x, y) => exp`    | ❌ ambíguo com parênteses         | ✅ máxima                             | ✅                                     | ✅ livre           | precisa parênteses |
| D | `λx. λy. => exp`   |                                   |                                       |                                        |                    |                    |

Exemplos concretos de aplicação para cada forma:

```text
A: (fn (x, y) => x + y)(2, 3)
B: ([x, y] => x + y)(2, 3)
C: [x, y => x + y](2, 3)
D: ((x, y) => x + y)(2, 3)   # o parser não sabe se '(' é lambda ou parêntese
E: (λx. λy. => x + y)(2, 3)
```

### 2.3 Discussão aberta

Perguntas-guia:

- Se escolhermos B ou C, o que acontece quando quisermos listas?
- O ganho de C (não precisar de parênteses na aplicação) compensa a perda de
tipos limpos?
- D é realmente problemática, ou o parser poderia dar conta com *lookahead*?
- E é a clássica notação chamada de _lambda cálculo_ (tratarei dela em separado)

Arbitremos com fatos, não com opiniões.

### 2.4 Votação e registro

Vamos decidir de forma coletiva em sala de aula.

```text
Decisão da turma: <forma escolhida>
Justificativa: <duas ou três razões>
Dívidas técnicas: <o que fica em aberto, se houver>
```

A decisão valerá para a próxima versão de `aljabr`; se se mostrar má escolha,
teremos que revisitá-la adiante, mas faremos registro da razão original.


## Bloco 3:  Sintaxe da forma escolhida

> Os exemplos abaixo assumem a opção A. Será preciso adaptar se a turma
> escolher outra. Fazer com a própria turma, como exercício coletivo.

### 3.1 Sintaxe concreta

```text
<exp>    ::= ... | fn (<params>) => <exp> | <exp> ( <args> )
<params> ::= ε | <param> | <param>, <params>
<args>   ::= ε | <exp> | <exp>, <args>
```

Exemplos canônicos:

```text
fn (x) => x * x
fn (x, y) => x + y
fn () => 42
```

### 3.2 Sintaxe abstrata

Dois novos nós na AST:

```text
Lambda(params, corpo)
App(funcao, args)
```

Exemplo de AST:

```text
App(Lambda(["x"], Mul(Var("x"), Var("x"))), [Num(3)])
```

### 3.3 Vinculação via `let`

Reaproveitar o `let` da Aula 08:

```text
let quad = fn (x) => x * x in
quad(3) + quad(5)
```

**Ponto importante:** o `let` não muda. Ele só passa a poder vincular um novo
tipo de valor.


## Bloco 4:  Semântica: de lambdas fechadas a closures

**Definições a introduzir, em ordem:**
1. Lambda fechada
2. Variável livre
3. Closure
4. Regra operacional de avaliação

### 4.1 Funções como lambdas fechadas

**Definição a apresentar:**

> Uma **lambda fechada** é uma função cujo corpo não menciona nenhuma variável
> que não esteja entre seus parâmetros.

Exemplo canônico:

```text
fn (x) => x * x
```

Aqui, `(params, corpo)` é representação **completa**. Avaliar o corpo em
ambiente novo, contendo apenas `x ↦ v`.

**Observação a fazer:** essa é a noção de função que todo aluno conhece da
matemática do ensino médio. Nada de novo ainda.

### 4.2 Lambdas com variáveis livres

**Definição a apresentar:**

> Uma variável é **livre** em relação a uma lambda se ela não é um dos
> parâmetros e não está ligada por um `let` dentro do corpo da lambda.

Exemplo:

```text
fn (x) => x + a
```

Aqui `a` é livre. Perguntar à turma se o que fariam se tivessem que avaliar,
por exemplo, o valor da aplicação dessa função a, digamos 1. Aqui é importante
que o aluno veja que o corpo menciona `a`, mas `a` não está nos parâmetros.
Onde o avaliador deve ir buscar `a`?

A ideia é ir buscar em _contexto_. Assume-se que $a$ é livre na expressão
lambda, mas que deve ser vinculada em algum momento, para que a avaliação
efetiva se dê.

**Ponto central:** o modelo `(params, corpo)` **não tem resposta** para essa
pergunta. Aqui está a lacuna.

**Reforçar:** em `let a = 10 in fn (x) => x + a`, `a` é livre *em
relação à lambda*, mas ligada *no programa inteiro*. O que importa aqui é
"livre em relação à lambda", não "livre no programa".

> Uma variável é dita _livre_ em uma expressão lambda se não é um dos
> parâmetros formais.

### 4.3 Demo em Python 

**Objetivo:** mostrar que o fenômeno existe, tem nome e é comum.

```python
def cria_somador(n):
    def somador(x):
        return x + n
    return somador

soma5 = cria_somador(5)
print(soma5(3))   # 8
```

Aspecto a ressaltar aqui:

> `soma5` ainda funciona depois que `cria_somador` retornou. Onde está o `5`?  Ele
> não está nos parâmetros nem no corpo.

**Nomear:** isso é um **closure**. O `5` foi capturado (enclausurado) no
ambiente de criação. Python escolheu *capturar o ambiente de criação*.
IMPORTANTE: Python não usou o ambiente de chamada.


### 4.4 O closure como tripla

**Definição a apresentar:**

> O valor de uma lambda é uma **closure**: uma tripla `(parâmetros, corpo,
> ambiente de criação)`.

- **Parâmetros**: os nomes a serem ligados na aplicação.
- **Corpo**: a expressão a ser avaliada. É a "computação pendente".
- **Ambiente de criação**: o `ρ` ativo quando a lambda foi avaliada. É o que
permite à função "lembrar" de valores externos.

Reavaliar o exemplo do `a = 10`:

```text
let a = 10 in
let f = fn (x) => x + a in
f(5)   # 15
```

Mostrar que, com o ambiente de criação capturado, `a` é resolvido corretamente.

**Mencionar de passagem a alternativa:**

> Uma outra forma de resolver `a` seria consultar o ambiente de quem chama, no
> momento da aplicação. Isso se chama **escopo dinâmico**. Vamos discutir na
> Aula 11 por que não é o que queremos.

### 4.5 Regra operacional informal

```text
Avaliar Lambda([p₁, ..., pₙ], corpo) em ρ  ⟹  Closure([p₁, ..., pₙ], corpo, ρ)

Avaliar App(f, [a₁, ..., aₘ]) em ρ:
   1. Avaliar f em ρ              ⟹  Closure([p₁, ..., pₙ], corpo, ρ₀)
   2. Se m ≠ n, erro de aridade
   3. Avaliar aᵢ em ρ              ⟹  vᵢ    (para i = 1..n)
   4. Avaliar corpo em ρ₀[p₁ ↦ v₁, ..., pₙ ↦ vₙ]
```

Enfatizar o `ρ₀` (ambiente de criação) no passo 4. É o coração do closure.

### 4.6 Rastreando ambientes: um exemplo com variável livre

**Objetivo:** deixar explícito, com um exemplo concreto, que `ρ_criação` e
`ρ_chamada` são **ambientes diferentes**, capturados em **momentos
diferentes**. É aqui que a confusão entre os dois nomes se desfaz.

```text
let n = 7 in
let soma_n = fn (x) => x + n in
let n = 100 in
soma_n(3)
```

**Pergunta à turma, antes de rastrear:**

> Qual é o resultado: `10` ou `103`?

Deixar a turma responder antes de mostrar. A resposta correta é `10`. O `n` que
a lambda enxerga é o do **momento em que ela foi criada**, não o do momento em
que foi chamada.

**Rastreamento passo a passo:**

Numerar cada passo no quadro, com a notação de ambientes à direita.

```text
1. Avaliar 7 em ρ₀                          ⟹  7
   ρ₁ = ρ₀[n ↦ 7]

2. Avaliar fn (x) => x + n em ρ₁
   ⟹  Closure(["x"], Var("x") + Var("n"), ρ₁)
                                              ↑
                                    ρ_criação = ρ₁ = { n ↦ 7 }

   ρ₂ = ρ₁[soma_n ↦ Closure(...)]

3. Estender com n = 100:
   ρ₃ = ρ₂[n ↦ 100]

4. Avaliar soma_n em ρ₃ (ρ_chamada)
   ⟹  Closure(["x"], Var("x") + Var("n"), ρ₁)
                                              ↑
                                    ρ_criação ainda é ρ₁, não ρ₃

5. Avaliar 3 em ρ₃                          ⟹  3

6. Avaliar corpo em ρ₁[x ↦ 3] = { n ↦ 7, x ↦ 3 }
   Var("x") + Var("n")  ⟹  3 + 7  ⟹  10
```

Aspectos a observar:

- **Passo 2:** o closure é criada com `ρ_criação = ρ₁`. Nesse momento, `n ↦ 7`.
- **Passo 4:** a aplicação acontece em `ρ_chamada = ρ₃`. Aqui, `n ↦ 100`. Mas o
`ρ_criação` do closure **não muda** — continua sendo `ρ₁`.
- **Passo 6:** o corpo é avaliado em `ρ_criação[x ↦ 3]`, não em `ρ_chamada[x ↦
3]`. Por isso o `n` que aparece é `7`, não `100`.

**Frase de fecho:**

> O `ρ_criação` não é o ambiente onde a expressão de aplicação é avaliada. Esse é
> ρ_chamada — o ambiente onde buscamos `f` e calculamos os argumentos. `ρ_criação`
> é o ambiente onde a lambda foi criada, e é ele que será usado, estendido com
> as ligações dos parâmetros, para avaliar o corpo da função. É por isso que
> `soma_n(3)` dá 10, e não 103.


**Contraste com escopo dinâmico (plantando a semente do Bloco 5):**

> "Se, no passo 6, tivéssemos usado `ρ_chamada[x ↦ 3]`, o resultado seria `100
> + 3 = 103`. Essa é a diferença entre escopo léxico e escopo dinâmico.
> Voltamos a isso em cinco minutos."


## Bloco 5:  Prévia: escopo léxico vs. dinâmico

### 5.1 A tensão

Perguntar:

> E se, em vez de usar `ρ₀` no passo 3, usássemos o ambiente de chamada `ρ`?

Exemplo mínimo:

```text
let a = 10 in
let f = fn (x) => x + a in
let a = 20 in
f(5)   # léxico: 15 | dinâmico: 25
```

**Anunciar:** essa diferença será o tema central da Aula 11. Por ora,
registrar: *"o `aljabr` usa escopo léxico; veremos por quê na Aula 11."*


## Bloco 6:  Fechamento, currying e ponte

### 6.1 Resumo

Recapitular as três conquistas da aula:

1. Decisão coletiva da sintaxe da lambda.
2. Lambda como novo valor: closure `(params, corpo, ambiente de criação)`.
3. Vinculação via `let`, com captura do ambiente de criação.

### 6.2 Envoi: currying

**Mostrar o exemplo antes de nomear:**

```text
fn (x) => fn (y) => x + y
```

Aplicação:

```text
(fn (x) => fn (y) => x + y)(2)(3)   --> 5
```

Equivalência:

```text
fn (x, y) => x + y   ≡   fn (x) => fn (y) => x + y
```

**Agora nomear:**

> Isso se chama **currying**, e é uma consequência de a lambda cálculo só ter
> lambdas de um parâmetro.

**Ponto crucial a enfatizar:** a lambda interna `fn (y) => x + y` é uma
**closure** cujo ambiente de criação inclui `x`. Sem isso, currying parece
mágica.

**Encerramento:**

> "A escolha que fizemos hoje,  múltiplos parâmetros,  é uma conveniência
> notacional. Poderíamos ter escolhido um parâmetro por vez, como faz o lambda
> cálculo, e ainda assim expressar tudo o que expressamos hoje. O que
> ganharíamos: regras semânticas um pouco mais simples. O que perderíamos:
> legibilidade. Veremos na Aula 10 como implementar isso, e aí a diferença fica
> concreta."

### 6.3 Ponte para a Aula 10

Anunciar: na próxima aula, o closure vira uma tripla Python concreta e o
avaliador é estendido para `Lambda` e `App`. A regra operacional do Bloco 4.5
será o roteiro da implementação.

### 6.4 Exercícios de fixação

Propor para entrega antes da Aula 10:

1. Escrever a AST de `fn (x, y) => x * x + y`.

2. Dado o programa abaixo, dizer o resultado e justificar (com base na
   closure):

   ```text
   let n = 7 in
     let soma_n = fn (x) => x + n in
       soma_n(3)
   ```

3. **(Desafio)** Modificar o programa acima para que, sob escopo **dinâmico**,
   o resultado mude. Explicar por quê.

4. **(Desafio extra)** Reescrever `fn (x, y, z) => x + y * z` na forma
   currificada. Explicar por que a lambda interna captura `x` e `y`.


## Pontos de checagem de entendimento

Verificar ao longo da aula:

- **Após o Bloco 2:** a turma consegue articular pelo menos dois critérios que
motivaram a escolha sintática?
- **Após o Bloco 3:** a turma consegue escrever a AST de uma lambda simples?
- **Após o Bloco 4.2:** a turma identifica a variável livre em `fn (x) => x +
a`?
- **Após o Bloco 4.4:** a turma explica por que o closure precisa do terceiro
componente (ambiente de criação)?
- **Após o Bloco 5:** a turma percebe que escopo léxico vs. dinâmico é uma
**decisão**, não um fato?
- **Após o Bloco 6:** a turma percebe que currying é consequência do closure,
não tópico separado?
